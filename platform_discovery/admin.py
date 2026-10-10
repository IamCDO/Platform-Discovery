from django.contrib import admin

from .models import Business, BusinessApplication, BusinessCategory, Order, OrderItem, Product


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "business_id", "owner", "category", "status", "location")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("name", "business_id", "owner__username")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "price", "discount_percent", "stock", "is_available")
    list_filter = ("is_available", "business")
    search_fields = ("name", "business__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "status", "total_amount", "created_at")
    list_filter = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("product", "business", "quantity", "unit_price", "discount_percent")
    search_fields = ("product__name", "business__name")


@admin.register(BusinessApplication)
class BusinessApplicationAdmin(admin.ModelAdmin):
    list_display = ("business_name", "applicant", "category", "status", "submitted_at")
    list_filter = ("status", "category")
    search_fields = ("business_name", "applicant__username")
