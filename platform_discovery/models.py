import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class BusinessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, default='')

    CATEGORY_IMAGES = {
        'clothing': 'https://images.unsplash.com/photo-1788035962539-a1d6ef60ec48?auto=format&fit=crop&w=900&q=80',
        'food-drinks': 'https://images.unsplash.com/photo-1664992960082-0ea299a9c53e?auto=format&fit=crop&w=900&q=80',
        'school-materials': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=900&q=80',
        'technology': 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
    }

    class Meta:
        ordering = ["name"]

    @property
    def default_image_url(self):
        return self.image_url or self.CATEGORY_IMAGES.get(self.slug, 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while BusinessCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Business(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_business")
    category = models.ForeignKey(BusinessCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="businesses")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    business_id = models.CharField(max_length=20, unique=True, editable=False)
    location = models.CharField(max_length=200, default="Online", help_text="Use 'Online' if there is no physical branch.")
    image_url = models.URLField(blank=True, default='')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_featured = models.BooleanField(default=False)
    approval_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.business_id:
            while True:
                candidate = f"BUS-{uuid.uuid4().hex[:8].upper()}"
                if not Business.objects.filter(business_id=candidate).exists():
                    self.business_id = candidate
                    break

        base_slug = slugify(self.slug or self.name) or "business"
        slug = base_slug
        counter = 1
        while Business.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

        super().save(*args, **kwargs)

    @property
    def display_location(self):
        return self.location or "Online"

    @property
    def default_image_url(self):
        if self.image_url:
            return self.image_url
        category_slug = self.category.slug if self.category else 'technology'
        category_images = BusinessCategory.CATEGORY_IMAGES
        return category_images.get(category_slug, 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80')

    def __str__(self):
        return self.name


class Product(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    image_url = models.URLField(blank=True, default='')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        base_slug = slugify(self.slug or self.name) or "product"
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        super().save(*args, **kwargs)

    @property
    def default_image_url(self):
        if self.image_url:
            return self.image_url
        if self.business.category and self.business.category.slug == 'food-drinks':
            food_images = {
                'wrap': 'https://images.unsplash.com/photo-1765584830134-12d879ad13bd?auto=format&fit=crop&w=900&q=80',
                'coffee': 'https://images.unsplash.com/photo-1561742727-74fee4d4de60?auto=format&fit=crop&w=900&q=80',
                'latte': 'https://images.unsplash.com/photo-1561742727-74fee4d4de60?auto=format&fit=crop&w=900&q=80',
                'burger': 'https://images.unsplash.com/photo-1765584830134-12d879ad13bd?auto=format&fit=crop&w=900&q=80',
                'snack': 'https://images.unsplash.com/photo-1664992960082-0ea299a9c53e?auto=format&fit=crop&w=900&q=80',
            }
            for key, value in food_images.items():
                if key in self.name.lower():
                    return value
            return BusinessCategory.CATEGORY_IMAGES['food-drinks']
        if self.business.category and self.business.category.slug == 'clothing':
            return BusinessCategory.CATEGORY_IMAGES['clothing']
        keyword = self.name.lower()
        fallback_map = {
            'coffee': 'https://images.unsplash.com/photo-1561742727-74fee4d4de60?auto=format&fit=crop&w=900&q=80',
            'latte': 'https://images.unsplash.com/photo-1561742727-74fee4d4de60?auto=format&fit=crop&w=900&q=80',
            'shirt': BusinessCategory.CATEGORY_IMAGES['clothing'],
            'dress': BusinessCategory.CATEGORY_IMAGES['clothing'],
            'ankara': BusinessCategory.CATEGORY_IMAGES['clothing'],
            'agbada': BusinessCategory.CATEGORY_IMAGES['clothing'],
            'laptop': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80',
            'usb': 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
            'notebook': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80',
            'book': 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=900&q=80',
            'burger': 'https://images.unsplash.com/photo-1765584830134-12d879ad13bd?auto=format&fit=crop&w=900&q=80',
            'snack': 'https://images.unsplash.com/photo-1664992960082-0ea299a9c53e?auto=format&fit=crop&w=900&q=80',
            'charger': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=80',
        }
        for key, value in fallback_map.items():
            if key in keyword:
                return value
        return 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80'

    @property
    def discounted_price(self):
        if self.discount_percent > 0:
            discount_fraction = Decimal(self.discount_percent) / Decimal("100")
            return self.price * (Decimal("1") - discount_fraction)
        return self.price

    @property
    def savings_amount(self):
        return self.price - self.discounted_price

    @property
    def has_discount(self):
        return self.discount_percent > 0

    def __str__(self):
        return f"{self.business.name} - {self.name}"


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    session_key = models.CharField(max_length=40, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class BusinessApplication(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="business_applications")
    business_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    matriculation_number = models.CharField(max_length=50, default="N/A")
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    category = models.ForeignKey(BusinessCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")
    location = models.CharField(max_length=200, default="Online")
    site_url = models.URLField(blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_applications")
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.business_name} ({self.status})"
