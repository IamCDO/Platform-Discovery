from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify

from .forms import BusinessApplicationForm, ProductForm, UserRegisterForm
from .models import Business, BusinessApplication, BusinessCategory, Order, OrderItem, Product


def get_cart(request):
    return request.session.get("cart", {})


def get_cart_items(request):
    cart = get_cart(request)
    items = []
    total = Decimal("0")

    for product_id, quantity in cart.items():
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        if quantity <= 0:
            continue
        product = Product.objects.select_related("business").filter(pk=int(product_id), is_available=True).first()
        if not product:
            continue
        line_total = product.discounted_price * quantity
        total += line_total
        items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
            "discounted_price": product.discounted_price,
        })
    return items, total


def home(request):
    categories = BusinessCategory.objects.all()
    featured_businesses = Business.objects.filter(status=Business.STATUS_APPROVED, is_featured=True)[:6]
    featured_products = Product.objects.filter(is_available=True, business__status=Business.STATUS_APPROVED)[:8]
    return render(request, "platform_discovery/home.html", {
        "categories": categories,
        "featured_businesses": featured_businesses,
        "featured_products": featured_products,
    })


def categories(request):
    category_list = BusinessCategory.objects.prefetch_related("businesses").all()
    return render(request, "platform_discovery/categories.html", {"categories": category_list})


def category_detail(request, slug):
    category = get_object_or_404(BusinessCategory, slug=slug)
    businesses = Business.objects.filter(category=category, status=Business.STATUS_APPROVED)
    search_term = request.GET.get("q", "").strip()
    if search_term:
        businesses = businesses.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))
    return render(request, "platform_discovery/category_detail.html", {
        "category": category,
        "businesses": businesses,
        "search_term": search_term,
    })


def business_detail(request, slug):
    business = get_object_or_404(Business, slug=slug, status=Business.STATUS_APPROVED)
    products = business.products.filter(is_available=True)
    search_term = request.GET.get("q", "").strip()
    if search_term:
        products = products.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))
    return render(request, "platform_discovery/business_detail.html", {
        "business": business,
        "products": products,
        "search_term": search_term,
    })


def search_results(request):
    query = request.GET.get("q", "").strip()
    businesses = Business.objects.none()
    products = Product.objects.none()
    if query:
        businesses = Business.objects.filter(status=Business.STATUS_APPROVED).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        products = Product.objects.filter(
            is_available=True,
            business__status=Business.STATUS_APPROVED,
        ).filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, "platform_discovery/search_results.html", {
        "query": query,
        "businesses": businesses,
        "products": products,
    })


@login_required
def register_business(request):
    if getattr(request.user, "owned_business", None):
        messages.warning(request, "You already have a registered business on the platform.")
        return redirect("business_dashboard")

    if request.method == "POST":
        form = BusinessApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.location = application.location.strip() or "Online"
            application.save()

            student_affairs_email = getattr(settings, "STUDENT_AFFAIRS_EMAIL", "studentaffairs@example.com")
            send_mail(
                subject="New business registration submitted",
                message=(
                    f"A new student business application has been submitted by {request.user.get_full_name() or request.user.username}.\n"
                    f"Business name: {application.business_name}\n"
                    f"Category: {application.category}\n"
                    f"Location: {application.location}\n"
                    f"Please review it in the student affairs dashboard."
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
                recipient_list=[student_affairs_email],
                fail_silently=True,
            )
            messages.success(request, "Your business registration has been submitted and is pending review.")
            return redirect("my_applications")
    else:
        form = BusinessApplicationForm()

    return render(request, "platform_discovery/register_business.html", {"form": form})


def profile(request, default_mode="login"):
    mode = request.POST.get("mode") or request.GET.get("mode") or default_mode
    if mode not in {"login", "signup"}:
        mode = "login"
    next_url = request.POST.get("next") or request.GET.get("next", "")

    if mode == "signup":
        form = UserRegisterForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. You can now register a business and place orders.")
            return redirect("register_business")
    else:
        form = AuthenticationForm(request, data=request.POST if request.method == "POST" else None)
        if request.method == "POST" and form.is_valid():
            login(request, form.get_user())
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect(settings.LOGIN_REDIRECT_URL)

    return render(request, "platform_discovery/profile.html", {
        "form": form,
        "mode": mode,
        "next": next_url,
    })


@login_required
def my_applications(request):
    applications = BusinessApplication.objects.filter(applicant=request.user)
    return render(request, "platform_discovery/my_applications.html", {"applications": applications})


@login_required
def business_portal(request):
    business = getattr(request.user, "owned_business", None)
    applications = BusinessApplication.objects.filter(applicant=request.user).order_by("-submitted_at")
    if business:
        products = Product.objects.filter(business=business)
        orders = OrderItem.objects.filter(business=business).select_related("order", "product")
    else:
        products = []
        orders = []
    return render(request, "platform_discovery/business_portal.html", {
        "business": business,
        "applications": applications,
        "products": products,
        "orders": orders,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product").order_by("-created_at")
    return render(request, "platform_discovery/my_orders.html", {"orders": orders})


@user_passes_test(lambda user: user.is_staff)
def student_affairs_dashboard(request):
    applications = BusinessApplication.objects.select_related("applicant", "category", "reviewed_by").order_by("-submitted_at")

    if request.method == "POST":
        application_id = request.POST.get("application_id")
        decision = request.POST.get("decision")
        notes = request.POST.get("review_notes", "")
        application = get_object_or_404(BusinessApplication, pk=application_id)

        if decision == "approve":
            if not Business.objects.filter(owner=application.applicant).exists():
                Business.objects.create(
                    owner=application.applicant,
                    category=application.category,
                    name=application.business_name,
                    slug=slugify(application.business_name),
                    location=application.location,
                    email=application.email,
                    phone_number=application.phone_number,
                    description=application.description,
                    status=Business.STATUS_APPROVED,
                    approval_note=notes,
                    approved_at=timezone.now(),
                )
            else:
                existing_business = Business.objects.get(owner=application.applicant)
                existing_business.category = application.category
                existing_business.name = application.business_name
                existing_business.slug = slugify(application.business_name) or "business"
                existing_business.location = application.location
                existing_business.email = application.email
                existing_business.phone_number = application.phone_number
                existing_business.description = application.description
                existing_business.status = Business.STATUS_APPROVED
                existing_business.approval_note = notes
                existing_business.approved_at = timezone.now()
                existing_business.save()

            send_mail(
                subject="Your business application has been approved",
                message=(
                    f"Congratulations! Your registration for {application.business_name} has been approved. "
                    "You can now sign in to your business dashboard and add products."
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
                recipient_list=[application.email],
                fail_silently=True,
            )
        elif decision == "reject":
            if Business.objects.filter(owner=application.applicant).exists():
                existing_business = Business.objects.get(owner=application.applicant)
                existing_business.status = Business.STATUS_REJECTED
                existing_business.approval_note = notes
                existing_business.save()

        application.status = decision
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.review_notes = notes
        application.save()
        messages.success(request, "Application status updated.")
        return redirect("student_affairs_dashboard")

    return render(request, "platform_discovery/student_affairs_dashboard.html", {"applications": applications})


@login_required
def business_dashboard(request):
    try:
        business = Business.objects.get(owner=request.user, status=Business.STATUS_APPROVED)
    except Business.DoesNotExist:
        messages.error(request, "Your business is not active yet or has not been approved.")
        return redirect("home")

    products = Product.objects.filter(business=business)
    orders = OrderItem.objects.filter(business=business).select_related("order", "product")
    return render(request, "platform_discovery/business_dashboard.html", {
        "business": business,
        "products": products,
        "orders": orders,
    })


@login_required
def create_product(request):
    try:
        business = Business.objects.get(owner=request.user, status=Business.STATUS_APPROVED)
    except Business.DoesNotExist:
        messages.error(request, "You must have an approved business before adding products.")
        return redirect("home")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = business
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect("business_dashboard")
    else:
        form = ProductForm()

    return render(request, "platform_discovery/product_form.html", {"form": form, "business": business, "mode": "create"})


@login_required
def edit_product(request, product_id):
    try:
        business = Business.objects.get(owner=request.user, status=Business.STATUS_APPROVED)
    except Business.DoesNotExist:
        messages.error(request, "You must have an approved business before editing products.")
        return redirect("home")

    product = get_object_or_404(Product, pk=product_id, business=business)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("business_dashboard")
    else:
        form = ProductForm(instance=product)

    return render(request, "platform_discovery/product_form.html", {"form": form, "business": business, "mode": "edit", "product": product})


def cart_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            product_id = int(request.POST.get("product_id", ""))
        except (TypeError, ValueError):
            product_id = None

        cart = dict(get_cart(request))
        if product_id is not None:
            product_key = str(product_id)
            try:
                quantity = int(cart.get(product_key, 0))
            except (TypeError, ValueError):
                quantity = 0
            product = Product.objects.filter(pk=product_id).first()

            if not product:
                cart.pop(product_key, None)
            elif action == "increase":
                if not product.is_available or quantity >= product.stock:
                    messages.error(request, f"Not enough stock available for {product.name}.")
                else:
                    cart[product_key] = quantity + 1
            elif action == "decrease":
                if quantity <= 1:
                    cart.pop(product_key, None)
                else:
                    cart[product_key] = quantity - 1

            request.session["cart"] = cart
            request.session.modified = True
        return redirect("cart")

    items, total = get_cart_items(request)
    return render(request, "platform_discovery/cart.html", {"cart_items": items, "total": total, "cart_count": sum(item["quantity"] for item in items)})


def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("cart")

    product = get_object_or_404(Product, pk=product_id, is_available=True)
    cart = get_cart(request)
    current_quantity = int(cart.get(str(product.id), 0))
    next_quantity = current_quantity + 1

    if next_quantity > product.stock:
        return JsonResponse({"message": "Not enough stock available.", "cart_count": sum(cart.values())}, status=400)

    cart[str(product.id)] = next_quantity
    request.session["cart"] = cart
    request.session.modified = True
    cart_count = sum(cart.values())
    return JsonResponse({"message": "Added to cart", "cart_count": cart_count})


@login_required
def checkout(request):
    items, total = get_cart_items(request)
    if request.method == "POST":
        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        order = Order.objects.create(
            user=request.user,
            session_key=request.session.session_key,
            total_amount=0,
            status=Order.STATUS_PAID,
        )

        for item in items:
            product = item["product"]
            quantity = item["quantity"]
            if quantity > product.stock:
                messages.error(request, f"Not enough stock for {product.name}.")
                return redirect("cart")

            product.stock -= quantity
            if product.stock <= 0:
                product.is_available = False
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                business=product.business,
                quantity=quantity,
                unit_price=product.discounted_price,
                discount_percent=product.discount_percent,
            )
            order.total_amount += product.discounted_price * quantity

        order.save()

        for item in items:
            product = item["product"]
            business = product.business
            send_mail(
                subject=f"New order received for {business.name}",
                message=(
                    f"You have received a new order for {item['product'].name}.\n"
                    f"Quantity: {item['quantity']}\n"
                    f"Customer email: {request.user.email if request.user.is_authenticated else 'Guest'}\n"
                    f"Please check your business dashboard for full details."
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
                recipient_list=[business.email],
                fail_silently=True,
            )

        request.session["cart"] = {}
        request.session.modified = True
        messages.success(request, "Payment confirmed. Order placed successfully.")
        return redirect("home")

    return render(request, "platform_discovery/checkout.html", {"cart_items": items, "total": total})


def search(request):
    return redirect("search_results")
