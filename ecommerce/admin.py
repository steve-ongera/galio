from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from django.utils import timezone
from .models import (
    User, Address, Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, ProductVariant, 
    ProductVariantAttribute, Review, ReviewImage, Wishlist, 
    WishlistItem, Cart, CartItem, Coupon, Order, OrderItem, 
    Newsletter, ProductView, RecentlyViewedProduct, SiteSetting, 
    Banner
)


# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'date_of_birth', 'avatar', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'phone', 'date_of_birth', 'avatar', 'is_verified')
        }),
    )

from django.contrib import admin
from .models import County, DeliveryArea


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(DeliveryArea)
class DeliveryAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "county", "shipping_fee", "delivery_days", "is_active", "created_at")
    list_filter = ("county", "is_active")
    search_fields = ("name", "county__name")
    ordering = ("county__name", "name")


# Address Admin
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['address_type', 'first_name', 'last_name' , 'country', 'is_default']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'full_name', 'is_default']
    list_filter = ['address_type',  'is_default']
    search_fields = ['user__email', 'first_name', 'last_name' ]
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'sort_order', 'product_count', 'image_preview']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'


from django.contrib import admin
from django.utils.html import format_html

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count', 'logo_preview']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        # Method 1: Use the default reverse relationship
        try:
            return obj.product_set.count()
        except AttributeError:
            # Method 2: Try custom related name if you defined one
            try:
                return obj.products.count()
            except AttributeError:
                # Method 3: Manual query if relationship is broken
                from .models import Product
                return Product.objects.filter(brand=obj).count()
    
    product_count.short_description = 'Products'
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = 'Logo'

# Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


# Product Variant Inline
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'stock_quantity', 'is_active']


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 
        'status', 'is_featured', 'is_hot_deal', 'is_big_sale', 
        'is_best_seller', 'view_count', 'average_rating', 'created_at'
    ]
    list_filter = [
        'status', 'is_featured', 'is_hot_deal', 'is_big_sale', 
        'is_best_seller', 'category', 'brand', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    ordering = ['-created_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_inventory')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'dimensions_length', 'dimensions_width', 'dimensions_height'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status & Flags', {
            'fields': ('status', 'is_featured', 'is_hot_deal', 'is_big_sale', 'is_best_seller', 'is_digital', 'requires_shipping')
        }),
        ('Analytics', {
            'fields': ('view_count', 'sales_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    def average_rating(self, obj):
        return f"{obj.average_rating:.1f}" if obj.average_rating else "No ratings"
    average_rating.short_description = 'Avg Rating'
    
    actions = ['mark_as_featured', 'mark_as_hot_deal', 'mark_as_big_sale', 'mark_as_best_seller']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "Mark selected products as featured"
    
    def mark_as_hot_deal(self, request, queryset):
        queryset.update(is_hot_deal=True)
    mark_as_hot_deal.short_description = "Mark selected products as hot deals"
    
    def mark_as_big_sale(self, request, queryset):
        queryset.update(is_big_sale=True)
    mark_as_big_sale.short_description = "Mark selected products as big sale"
    
    def mark_as_best_seller(self, request, queryset):
        queryset.update(is_best_seller=True)
    mark_as_best_seller.short_description = "Mark selected products as best sellers"


# Product Attribute Admin
@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'value_count']
    prepopulated_fields = {'slug': ('name',)}
    
    def value_count(self, obj):
        return obj.values.count()
    value_count.short_description = 'Values'


# Product Attribute Value Admin
@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'color_preview']
    list_filter = ['attribute']
    search_fields = ['value']
    
    def color_preview(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color_code
            )
        return "No Color"
    color_preview.short_description = 'Color'


# Product Variant Admin
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'display_price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'product__category']
    search_fields = ['sku', 'product__name']


# Review Image Inline
class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'content']
    ordering = ['-created_at']
    
    inlines = [ReviewImageInline]
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Disapprove selected reviews"


# Wishlist Item Inline
class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_public', 'item_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['user__email', 'name']
    
    inlines = [WishlistItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# Cart Item Inline
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'session_key']
    
    inlines = [CartItemInline]


# Coupon Admin
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'usage_limit', 'is_valid_now', 'is_active']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    
    def is_valid_now(self, obj):
        return obj.is_valid()
    is_valid_now.boolean = True
    is_valid_now.short_description = 'Valid Now'


# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total_amount', 
        'payment_status', 'created_at', 'shipped_at', 'delivered_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at', 'shipped_at', 'delivered_at']
    search_fields = ['order_number', 'user__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Coupon', {
            'fields': ('coupon',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [OrderItemInline]
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped', shipped_at=timezone.now())
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered', delivered_at=timezone.now())
    mark_as_delivered.short_description = "Mark selected orders as delivered"


# Newsletter Admin
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at', 'unsubscribed_at']
    search_fields = ['email']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True, unsubscribed_at=None)
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


# Product View Admin
@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'product__category']
    search_fields = ['product__name', 'user__email', 'ip_address']
    readonly_fields = ['product', 'user', 'session_key', 'ip_address', 'user_agent', 'viewed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Recently Viewed Products Admin
@admin.register(RecentlyViewedProduct)
class RecentlyViewedProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['user', 'product', 'viewed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Site Setting Admin
@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description', 'updated_at']
    search_fields = ['key', 'description']
    
    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'


# Banner Admin
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'sort_order', 'valid_from', 'valid_to', 'image_preview']
    list_filter = ['is_active', 'valid_from', 'valid_to', 'created_at']
    search_fields = ['title', 'subtitle']
    ordering = ['sort_order', '-created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'
    
    actions = ['activate_banners', 'deactivate_banners']
    
    def activate_banners(self, request, queryset):
        queryset.update(is_active=True)
    activate_banners.short_description = "Activate selected banners"
    
    def deactivate_banners(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_banners.short_description = "Deactivate selected banners"

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'checkout_request_id',
        'order_link',
        'amount',
        'phone_number',
        'status_badge',
        'mpesa_receipt',
        'transaction_date',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_at',
        'updated_at',
        'transaction_date'
    ]
    
    search_fields = [
        'checkout_request_id',
        'mpesa_receipt',
        'phone_number',
        'order__order_number',
        'order__user__email'
    ]
    
    readonly_fields = [
        'checkout_request_id',
        'created_at',
        'updated_at',
        'formatted_raw_response'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'order',
                'checkout_request_id',
                'status',
                'amount'
            )
        }),
        ('M-Pesa Details', {
            'fields': (
                'mpesa_receipt',
                'phone_number',
                'transaction_date'
            )
        }),
        ('System Information', {
            'fields': (
                'created_at',
                'updated_at',
                'formatted_raw_response'
            ),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def order_link(self, obj):
        """Create a clickable link to the order"""
        if obj.order:
            url = reverse('admin:ecommerce_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'ecommerce__order_number'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'PENDING': 'orange',
            'SUCCESS': 'green',
            'FAILED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def formatted_raw_response(self, obj):
        """Format JSON response for better readability"""
        if obj.raw_response:
            try:
                formatted = json.dumps(obj.raw_response, indent=2)
                return format_html('<pre style="max-height: 300px; overflow: auto;">{}</pre>', formatted)
            except (TypeError, ValueError):
                return obj.raw_response
        return 'No response data'
    formatted_raw_response.short_description = 'Raw Response'
    
    def get_queryset(self, request):
        """Optimize queries"""
        queryset = super().get_queryset(request)
        return queryset.select_related('order', 'order__user')
    
    actions = ['mark_as_success', 'mark_as_failed', 'mark_as_pending']
    
    def mark_as_success(self, request, queryset):
        """Mark selected payments as successful"""
        updated = queryset.update(status='SUCCESS')
        self.message_user(request, f'{updated} payment(s) marked as successful.')
    mark_as_success.short_description = "Mark selected payments as successful"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected payments as failed"""
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'{updated} payment(s) marked as failed.')
    mark_as_failed.short_description = "Mark selected payments as failed"
    
    def mark_as_pending(self, request, queryset):
        """Mark selected payments as pending"""
        updated = queryset.update(status='PENDING')
        self.message_user(request, f'{updated} payment(s) marked as pending.')
    mark_as_pending.short_description = "Mark selected payments as pending"
    
    def has_add_permission(self, request):
        """Prevent manual creation of payments"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow deletion for failed payments or superusers"""
        if request.user.is_superuser:
            return True
        if obj and obj.status == 'FAILED':
            return True
        return False
    
# Customize Admin Site
admin.site.site_header = 'Ecommerce Admin'
admin.site.site_title = 'Ecommerce Admin Portal'
admin.site.index_title = 'Welcome to Ecommerce Administration'