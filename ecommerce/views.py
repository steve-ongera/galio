from django.shortcuts import render
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    Product, Category, Brand, Banner, 
    ProductView, RecentlyViewedProduct
)


def index(request):
    """Homepage view with all product sections"""
    
    # Get active banners
    banners = Banner.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now()
    ).order_by('sort_order')[:5]
    
    # Hot Deal Products (products with is_hot_deal=True and in stock)
    hot_deal_products = Product.objects.filter(
        is_hot_deal=True,
        status='active',
        stock_quantity__gt=0
    ).select_related('brand', 'category').prefetch_related('images')[:8]
    
    # Featured Products
    featured_products = Product.objects.filter(
        is_featured=True,
        status='active',
        stock_quantity__gt=0
    ).select_related('brand', 'category').prefetch_related('images')[:8]
    
    # Best Seller Products
    best_seller_products = Product.objects.filter(
        is_best_seller=True,
        status='active',
        stock_quantity__gt=0
    ).select_related('brand', 'category').prefetch_related('images')[:8]
    
    # New Arrivals (products created in last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_arrivals = Product.objects.filter(
        created_at__gte=thirty_days_ago,
        status='active',
        stock_quantity__gt=0
    ).select_related('brand', 'category').prefetch_related('images').order_by('-created_at')[:8]
    
    # Hot Sale Products (products with is_big_sale=True)
    hot_sale_products = Product.objects.filter(
        is_big_sale=True,
        status='active',
        stock_quantity__gt=0
    ).select_related('brand', 'category').prefetch_related('images')[:8]
    
    # Most Viewed Products (based on view_count)
    most_viewed_products = Product.objects.filter(
        status='active',
        stock_quantity__gt=0
    ).select_related('brand', 'category').prefetch_related('images').order_by('-view_count')[:8]
    
    popular_brands = Brand.objects.filter(
        is_active=True,
        product__status='active'
    ).annotate(
        product_count=Count('product'),
        total_views=Sum('product__view_count')
    ).order_by('-total_views', '-product_count')[:8]
    
    # Top Categories for navigation
    top_categories = Category.objects.filter(
        is_active=True,
        parent=None  # Only top-level categories
    ).order_by('sort_order', 'name')[:6]
    
    context = {
        'banners': banners,
        'hot_deal_products': hot_deal_products,
        'featured_products': featured_products,
        'best_seller_products': best_seller_products,
        'new_arrivals': new_arrivals,
        'hot_sale_products': hot_sale_products,
        'most_viewed_products': most_viewed_products,
        'popular_brands': popular_brands,
        'top_categories': top_categories,
    }
    
    return render(request, 'index.html', context)



from django.shortcuts import get_object_or_404, render
from .models import Product, ProductImage, Review, Category

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    images = product.images.all()
    primary_image = images.filter(is_primary=True).first()
    if not primary_image and images.exists():
        primary_image = images.first()
    
    reviews = product.reviews.filter(is_approved=True)
    average_rating = product.average_rating
    review_count = product.review_count
    
    # Get related products (from same category)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:8]
    
    # Get all categories for breadcrumb
    categories = []
    current_category = product.category
    while current_category:
        categories.insert(0, current_category)
        current_category = current_category.parent
    
    context = {
        'product': product,
        'images': images,
        'primary_image': primary_image,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'related_products': related_products,
        'categories': categories,
    }
    
    return render(request, 'products/product_detail.html', context)


from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product, Category, Brand

def product_list(request):
    # Get all active products
    products = Product.objects.filter(status='active').order_by('-created_at')
    
    # Get categories for sidebar
    categories = Category.objects.filter(is_active=True)
    
    # Get brands for manufacturer filter
    brands = Brand.objects.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(products, 16)  # Show 16 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'total_products': products.count(),
    }
    
    return render(request, 'products/product_list.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import User

# Your existing login view (with small improvements)
@csrf_protect
def login_view(request):
    """Handle user login"""
    # Redirect authenticated users
    if request.user.is_authenticated:
        next_page = request.GET.get('next', 'index')
        return redirect(next_page)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('rememberMe')

        # Validation
        if not email or not password:
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'auth/login.html')

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Handle remember me functionality
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Session expires when browser closes

                messages.success(request, f'Welcome back, {user.first_name or user.email}!')

                # Redirect to next page or dashboard
                next_page = request.GET.get('next', 'index')
                return redirect(next_page)
            else:
                messages.error(request, 'Your account has been disabled. Please contact support.')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    # Pass the next parameter to the template for hidden input
    context = {
        'next': request.GET.get('next', '')
    }
    return render(request, 'auth/login.html', context)


@csrf_protect
def register_view(request):
    """Handle user registration"""
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('index')  # Change to your desired redirect URL
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        subscribe_newsletter = request.POST.get('subnewsletter') == 'on'
        
        # Validation
        errors = []
        
        if not full_name:
            errors.append('Full name is required')
        
        if not email:
            errors.append('Email is required')
        elif not '@' in email or not '.' in email:
            errors.append('Please enter a valid email address')
        
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if password != password_confirm:
            errors.append('Passwords do not match')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists')
        
        # Check if username (email) already exists
        if User.objects.filter(username=email).exists():
            errors.append('An account with this email already exists')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'auth/register.html', {
                'full_name': full_name,
                'email': email,
                'subscribe_newsletter': subscribe_newsletter
            })
        
        try:
            # Split full name into first and last name
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Create new user
            user = User.objects.create(
                username=email,  # Use email as username
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password),
                is_verified=True,
            )
            
            # Auto-login after registration
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome {first_name}! Your account has been created successfully.')
                return redirect('account_profile')  
            else:
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, f'An error occurred during registration. Please try again.')
            return render(request, 'auth/register.html', {
                'full_name': full_name,
                'email': email,
                'subscribe_newsletter': subscribe_newsletter
            })
    
    return render(request, 'auth/register.html')


def logout_view(request):
    """Handle user logout"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# Optional: Password validation helper function
def validate_password(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if not any(c.isupper() for c in password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not any(c.islower() for c in password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not any(c.isdigit() for c in password):
        errors.append('Password must contain at least one number')
    
    return errors


# Enhanced register view with stronger password validation (optional)
@csrf_protect
def register_view_enhanced(request):
    """Enhanced register view with stronger password validation"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        subscribe_newsletter = request.POST.get('subnewsletter') == 'on'
        
        # Validation
        errors = []
        
        if not full_name:
            errors.append('Full name is required')
        
        if not email:
            errors.append('Email is required')
        elif not '@' in email or not '.' in email:
            errors.append('Please enter a valid email address')
        
        if not password:
            errors.append('Password is required')
        else:
            # Use enhanced password validation
            password_errors = validate_password(password)
            errors.extend(password_errors)
        
        if password != password_confirm:
            errors.append('Passwords do not match')
        
        if User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'auth/register.html', {
                'full_name': full_name,
                'email': email,
                'subscribe_newsletter': subscribe_newsletter
            })
        
        try:
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password)
            )
            
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome {first_name}! Your account has been created successfully.')
                return redirect('dashboard')
            else:
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'auth/register.html', {
                'full_name': full_name,
                'email': email,
                'subscribe_newsletter': subscribe_newsletter
            })
    
    return render(request, 'auth/register.html')

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Category, Brand, Product


def category_products(request, slug):
    """View to display products in a specific category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get products in this category and its subcategories
    products = Product.objects.filter(
        Q(category=category) | Q(category__parent=category),
        status='active'
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Handle sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['name', '-name', 'price', '-price', '-created_at', 'created_at', '-view_count']
    if sort_by in valid_sorts:
        products = products.order_by(sort_by)
    
    # Get all subcategories
    subcategories = Category.objects.filter(parent=category, is_active=True)
    
    # Get product counts for sidebar
    featured_count = products.filter(is_featured=True).count()
    hot_deal_count = products.filter(is_hot_deal=True).count()
    best_seller_count = products.filter(is_best_seller=True).count()
    sale_count = products.filter(compare_price__gt=0).count()
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'subcategories': subcategories,
        'page_obj': page_obj,
        'total_products': products.count(),
        'featured_count': featured_count,
        'hot_deal_count': hot_deal_count,
        'best_seller_count': best_seller_count,
        'sale_count': sale_count,
        'current_sort': sort_by,
    }
    
    return render(request, 'category/category_products.html', context)

def brand_products(request, slug):
    """View to display products from a specific brand"""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    
    products = Product.objects.filter(
        brand=brand,
        status='active'
    ).select_related('category', 'brand').prefetch_related('images')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'products': page_obj,
        'page_obj': page_obj,
        'total_products': products.count(),
    }
    
    return render(request, 'brands/brand_products.html', context)


def all_categories(request):
    """View to display all categories"""
    categories = Category.objects.filter(is_active=True).select_related('parent')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'category/all_categories.html', context)


def all_brands(request):
    """View to display all brands"""
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'brands': brands,
    }
    
    return render(request, 'brands/all_brands.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Product
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem, Coupon
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Cart, CartItem, Coupon  # Adjust imports based on your models

def cart_view(request):
    # Get cart items properly - replace this with your actual cart logic
    cart_items = []
    if request.user.is_authenticated:
        # For authenticated users
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
        except Cart.DoesNotExist:
            cart_items = []
    else:
        # For anonymous users using session
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                cart_items = CartItem.objects.filter(cart=cart)
            except Cart.DoesNotExist:
                cart_items = []
    
    # Handle coupon application if submitted
    if request.method == 'POST' and 'coupon_code' in request.POST:
        coupon_code = request.POST.get('coupon_code').strip()
        try:
            coupon = Coupon.objects.get(
                code__iexact=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            
            # Check if coupon has usage limit
            if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                messages.error(request, "This coupon has reached its usage limit.")
            else:
                # Store coupon in session
                request.session['applied_coupon'] = {
                    'code': coupon.code,
                    'discount_type': coupon.discount_type,
                    'discount_value': float(coupon.discount_value),
                    'minimum_amount': float(coupon.minimum_amount) if coupon.minimum_amount else None,
                    'maximum_discount': float(coupon.maximum_discount) if coupon.maximum_discount else None,
                }
                messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
                
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
        
        return redirect('cart')
    
    # Calculate totals with potential coupon discount
    cart_subtotal = sum(item.total_price for item in cart_items) if cart_items else Decimal('0.00')
    shipping_cost = Decimal('0.00')  # Add your shipping calculation logic here
    
    # Check for applied coupon
    coupon_discount = Decimal('0.00')
    coupon_code = None
    applied_coupon = request.session.get('applied_coupon')
    
    if applied_coupon and cart_subtotal > 0:
        coupon_code = applied_coupon['code']
        if applied_coupon['discount_type'] == 'percentage':
            # Calculate percentage discount
            discount = (cart_subtotal * Decimal(str(applied_coupon['discount_value']))) / Decimal('100')
            if applied_coupon['maximum_discount']:
                discount = min(discount, Decimal(str(applied_coupon['maximum_discount'])))
            coupon_discount = discount
        else:
            # Fixed amount discount
            coupon_discount = Decimal(str(applied_coupon['discount_value']))
        
        # Check minimum amount requirement
        if applied_coupon['minimum_amount'] and cart_subtotal < Decimal(str(applied_coupon['minimum_amount'])):
            messages.warning(request, f"Coupon requires minimum purchase of ${applied_coupon['minimum_amount']}")
            del request.session['applied_coupon']
            coupon_discount = Decimal('0.00')
            coupon_code = None
    
    # Ensure cart_total doesn't go negative
    cart_total = max(cart_subtotal + shipping_cost - coupon_discount, Decimal('0.00'))
    
    # Prepare context
    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'shipping_cost': shipping_cost,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_code,
        'cart_total': cart_total,
    }
    
    return render(request, 'cart/cart.html', context)


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import urlencode

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        # Get current URL and querystring (if any)
        current_url = request.get_full_path()
        login_url = reverse('login')  # replace with your actual login URL name
        return redirect(f"{login_url}?{urlencode({'next': current_url})}")
    
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant_id')  # If you have variants

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant_id=variant_id if variant_id else None,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart')

def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        # Add your coupon validation logic here
        # You might want to store the coupon in the session
        return redirect('cart')
    return redirect('cart')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.urls import reverse
from decimal import Decimal
import requests
import base64
import json
from datetime import datetime
import uuid
import logging
from .models import Cart, CartItem, Order, OrderItem, Address, Coupon, User, County, DeliveryArea
from .forms import CheckoutForm, BillingAddressForm, ShippingAddressForm, AddressSelectionForm
from .models import Payment
from django.views.decorators.http import require_POST , require_GET
from .models import Cart, CartItem, Order, OrderItem, Address, Coupon, User
from .forms import CheckoutForm, BillingAddressForm, ShippingAddressForm
from .models import Payment

# Set up logging for M-Pesa debugging
logger = logging.getLogger(__name__)

class CheckoutView(View):
    template_name = 'checkout.html'
    
    def get(self, request):
        logger.info(f"CheckoutView GET request from user: {request.user}")
        
        # Get or create cart
        cart = self.get_cart(request)
        
        if not cart or not cart.items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart')
        
        # Get user addresses if authenticated
        billing_addresses = []
        shipping_addresses = []
        if request.user.is_authenticated:
            billing_addresses = Address.objects.filter(user=request.user, address_type='billing')
            shipping_addresses = Address.objects.filter(user=request.user, address_type='shipping')
        
        # Initialize forms
        billing_form = BillingAddressForm()
        shipping_form = ShippingAddressForm()
        address_selection_form = None
        
        if request.user.is_authenticated:
            address_selection_form = AddressSelectionForm(user=request.user)
        
        # Get counties and their delivery areas for dropdown population
        counties = County.objects.filter(is_active=True).prefetch_related(
            'delivery_areas'
        ).order_by('name')
        
        # Create a structured data for counties and areas
        # Get counties and their delivery areas for dropdown population
        counties = County.objects.filter(is_active=True).prefetch_related(
            'delivery_areas'
        ).order_by('name')

        # Create a structured data for counties and areas
        counties_data = []
        for county in counties:
            areas = county.delivery_areas.filter(is_active=True).order_by('name')
            county_data = {
                'id': str(county.id),  # Convert to string for consistency
                'name': county.name,
                'areas': [{
                    'id': str(area.id),  # Convert to string for consistency
                    'name': area.name,
                    'shipping_fee': float(area.shipping_fee),
                    'delivery_days': area.delivery_days,
                    'display_name': f"{area.name} (KSh {area.shipping_fee} - {area.delivery_days} day{'s' if area.delivery_days > 1 else ''})"
                } for area in areas]
            }
            counties_data.append(county_data)

        print(f"Counties data prepared: {len(counties_data)} counties")  # Debug line
        for county in counties_data:
            print(f"County: {county['name']} has {len(county['areas'])} areas")  # Debug line
        
        # Calculate initial totals
        subtotal = cart.total_price
        shipping_cost = Decimal('0.00')
        tax_amount = self.calculate_tax(cart)
        total_amount = subtotal + shipping_cost + tax_amount
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'billing_form': billing_form,
            'shipping_form': shipping_form,
            'address_selection_form': address_selection_form,
            'billing_addresses': billing_addresses,
            'shipping_addresses': shipping_addresses,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'counties': counties,
            'counties_data': json.dumps(counties_data),  # JSON data for JavaScript
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        logger.info(f"CheckoutView POST request from user: {request.user}")
        logger.debug(f"POST data: {request.POST}")
        
        cart = self.get_cart(request)
        
        if not cart or not cart.items.exists():
            logger.error("Cart is empty during checkout")
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
        
        # Check if user selected existing address
        selected_billing_address = None
        selected_shipping_address = None
        
        if request.user.is_authenticated:
            billing_address_id = request.POST.get('billing_address_selection')
            shipping_address_id = request.POST.get('shipping_address_selection')
            
            if billing_address_id and billing_address_id != 'new':
                try:
                    selected_billing_address = Address.objects.get(
                        id=billing_address_id, user=request.user, address_type='billing'
                    )
                except Address.DoesNotExist:
                    pass
            
            if shipping_address_id and shipping_address_id != 'new':
                try:
                    selected_shipping_address = Address.objects.get(
                        id=shipping_address_id, user=request.user, address_type='shipping'
                    )
                except Address.DoesNotExist:
                    pass
        
        # Determine which forms to validate
        billing_form = None
        shipping_form = None
        
        if not selected_billing_address:
            billing_form = BillingAddressForm(request.POST, prefix='billing')
        
        ship_to_different = request.POST.get('ship_to_different') == 'on'
        if ship_to_different and not selected_shipping_address:
            shipping_form = ShippingAddressForm(request.POST, prefix='shipping')
        
        # Validate forms if needed
        forms_valid = True
        if billing_form and not billing_form.is_valid():
            forms_valid = False
            logger.error(f"Billing form errors: {billing_form.errors}")
        
        if shipping_form and not shipping_form.is_valid():
            forms_valid = False
            logger.error(f"Shipping form errors: {shipping_form.errors}")
        
        if forms_valid:
            try:
                with transaction.atomic():
                    # Create or get user
                    user = self.get_or_create_user(request, billing_form, selected_billing_address)
                    logger.info(f"User for order: {user}")
                    
                    # Get or create addresses
                    billing_address = selected_billing_address or self.create_address_from_form(
                        user, billing_form
                    )
                    
                    if ship_to_different:
                        shipping_address = selected_shipping_address or self.create_address_from_form(
                            user, shipping_form, 'shipping'
                        )
                    else:
                        shipping_address = billing_address
                    
                    # Calculate amounts with actual shipping cost
                    subtotal = cart.total_price
                    shipping_cost = shipping_address.delivery_area.shipping_fee
                    tax_amount = self.calculate_tax(cart)
                    discount_amount = self.apply_coupon(request, subtotal)
                    total_amount = subtotal + shipping_cost + tax_amount - discount_amount
                    
                    logger.info(f"Order amounts - Subtotal: {subtotal}, Shipping: {shipping_cost}, Tax: {tax_amount}, Discount: {discount_amount}, Total: {total_amount}")
                    
                    # Create order
                    order = Order.objects.create(
                        user=user,
                        subtotal=subtotal,
                        shipping_amount=shipping_cost,
                        tax_amount=tax_amount,
                        discount_amount=discount_amount,
                        total_amount=total_amount,
                        billing_address=self.format_address_object(billing_address),
                        shipping_address=self.format_address_object(shipping_address),
                        payment_method=request.POST.get('paymentmethod', 'mpesa'),
                    )
                    
                    logger.info(f"Order created: {order.order_number}")
                    
                    # Create order items
                    for cart_item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            variant=cart_item.variant,
                            quantity=cart_item.quantity,
                            unit_price=cart_item.unit_price,
                            total_price=cart_item.total_price
                        )
                        
                        # Update product stock
                        if cart_item.variant:
                            cart_item.variant.stock_quantity -= cart_item.quantity
                            cart_item.variant.save()
                        else:
                            cart_item.product.stock_quantity -= cart_item.quantity
                            cart_item.product.save()
                    
                    logger.info("Order items created and stock updated")
                    
                    # Handle payment
                    payment_method = request.POST.get('paymentmethod', 'mpesa')
                    logger.info(f"Payment method: {payment_method}")
                    
                    if payment_method == 'mpesa':
                        phone_number = self.clean_phone_number(billing_address.phone)
                        logger.info(f"Cleaned phone number: {phone_number}")
                        
                        if phone_number:
                            return self.initiate_mpesa_payment(request, order, phone_number)
                        else:
                            logger.error("Invalid phone number for M-Pesa payment")
                            messages.error(request, 'Valid phone number is required for M-Pesa payment.')
                            order.delete()
                            return self.get(request)
                    else:
                        # Handle other payment methods
                        logger.info(f"Non-M-Pesa payment method: {payment_method}")
                        # Clear cart after successful order creation
                        cart.items.all().delete()
                        cart.delete()
                        return redirect('order_confirmation', order_number=order.order_number)
                        
            except Exception as e:
                logger.exception(f"Error during checkout: {str(e)}")
                messages.error(request, f'An error occurred while processing your order: {str(e)}')
                return self.get(request)
        else:
            messages.error(request, 'Please correct the errors below.')
        
        # Re-render form with errors - need to get counties data again
        counties = County.objects.filter(is_active=True).prefetch_related(
            'delivery_areas'
        ).order_by('name')
        
        counties_data = []
        for county in counties:
            areas = county.delivery_areas.filter(is_active=True).order_by('name')
            county_data = {
                'id': str(county.id),  # Convert to string for consistency
                'name': county.name,
                'areas': [{
                    'id': str(area.id),  # Convert to string for consistency
                    'name': area.name,
                    'shipping_fee': float(area.shipping_fee),
                    'delivery_days': area.delivery_days,
                    'display_name': f"{area.name} (KSh {area.shipping_fee} - {area.delivery_days} day{'s' if area.delivery_days > 1 else ''})"
                } for area in areas]
            }
            counties_data.append(county_data)
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'billing_form': billing_form,
            'shipping_form': shipping_form,
            'subtotal': cart.total_price,
            'shipping_cost': Decimal('0.00'),
            'tax_amount': self.calculate_tax(cart),
            'total_amount': self.calculate_total(cart),
            'counties': counties,
            'counties_data': json.dumps(counties_data),
        }
        
        return render(request, self.template_name, context)
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key or request.session._get_or_create_session_key()
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart
    
    def get_or_create_user(self, request, billing_form, selected_billing_address):
        if request.user.is_authenticated:
            return request.user
        
        # Get user data from form or selected address
        if selected_billing_address:
            email = selected_billing_address.user.email
            first_name = selected_billing_address.first_name
            last_name = selected_billing_address.last_name
            phone = selected_billing_address.phone
        else:
            email = billing_form.cleaned_data.get('email')
            first_name = billing_form.cleaned_data.get('first_name', '')
            last_name = billing_form.cleaned_data.get('last_name', '')
            phone = billing_form.cleaned_data.get('phone', '')
        
        # Check if user wants to create account
        if request.POST.get('create_pwd'):
            password = request.POST.get('pwd')
            
            if User.objects.filter(email=email).exists():
                messages.info(request, 'An account with this email already exists.')
                return User.objects.get(email=email)
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            return user
        
        # For guest checkout, create a temporary user or handle differently
        if email and not User.objects.filter(email=email).exists():
            # Create a guest user (you might want to mark this differently)
            user = User.objects.create_user(
                username=f"guest_{uuid.uuid4().hex[:8]}",
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                is_active=False  # Mark as guest user
            )
            return user
        elif email and User.objects.filter(email=email).exists():
            return User.objects.get(email=email)
        
        raise ValueError("Cannot create user - insufficient data")
    
    def create_address_from_form(self, user, form):
        """Create address from validated form data"""
        if not form or not form.is_valid():
            raise ValueError("Form is not valid")
            
        address_type = 'billing' if form.prefix == 'billing' else 'shipping'
        
        address = Address.objects.create(
            user=user,
            address_type=address_type,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            phone=form.cleaned_data['phone'],
            county=form.cleaned_data['county'],
            delivery_area=form.cleaned_data['delivery_area'],
            detailed_address=form.cleaned_data['detailed_address']
        )
        
        return address
    
    def format_address_object(self, address):
        """Format address object as string for order"""
        return f"{address.first_name} {address.last_name}\n" \
               f"{address.detailed_address}\n" \
               f"{address.delivery_area.name}, {address.county.name}\n" \
               f"Kenya\n" \
               f"Phone: {address.phone}"
    
    def calculate_shipping(self, cart, delivery_area=None):
        """Calculate shipping cost based on delivery area"""
        if delivery_area:
            return delivery_area.shipping_fee
        return Decimal('0.00')
    
    def calculate_tax(self, cart):
        tax_rate = Decimal('0.00')  # Null/16% VAT in Kenya
        return cart.total_price * tax_rate
    
    def calculate_total(self, cart, shipping_cost=None):
        subtotal = cart.total_price
        shipping = shipping_cost or Decimal('0.00')
        tax = self.calculate_tax(cart)
        discount = self.apply_coupon_amount(cart)
        return subtotal + shipping + tax - discount
    
    def apply_coupon(self, request, subtotal):
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid():
                    if coupon.minimum_amount and subtotal < coupon.minimum_amount:
                        return Decimal('0.00')
                    
                    if coupon.discount_type == 'percentage':
                        discount = subtotal * (coupon.discount_value / 100)
                    else:
                        discount = coupon.discount_value
                    
                    if coupon.maximum_discount:
                        discount = min(discount, coupon.maximum_discount)
                    
                    return discount
            except Coupon.DoesNotExist:
                pass
        
        return Decimal('0.00')
    
    def apply_coupon_amount(self, cart):
        return Decimal('0.00')
    
    def clean_phone_number(self, phone):
        """Clean and format phone number for M-Pesa"""
        logger.info(f"Cleaning phone number: {phone}")
        
        if not phone:
            return None
        
        # Remove all non-digit characters
        phone = ''.join(filter(str.isdigit, str(phone)))
        logger.debug(f"Phone after removing non-digits: {phone}")
        
        # Handle Kenyan phone numbers
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+254'):
            phone = phone[1:]
        elif phone.startswith('254'):
            pass
        elif len(phone) == 9:
            phone = '254' + phone
        
        logger.debug(f"Phone after formatting: {phone}")
        
        # Validate length
        if len(phone) == 12 and phone.startswith('254'):
            logger.info(f"Valid phone number: {phone}")
            return phone
        
        logger.error(f"Invalid phone number format: {phone}")
        return None
    
    def initiate_mpesa_payment(self, request, order, phone_number):
        """Initiate M-Pesa STK Push"""
        logger.info(f"Initiating M-Pesa payment for order {order.order_number}, phone: {phone_number}, amount: {order.total_amount}")
        
        try:
            mpesa_service = MpesaService()
            response = mpesa_service.stk_push(
                phone_number=phone_number,
                amount=int(order.total_amount),
                account_reference=order.order_number,
                transaction_desc=f"Payment for order {order.order_number}"
            )
            
            logger.info(f"M-Pesa STK Push response: {response}")
            
            if response.get('ResponseCode') == '0':
                # Get checkout request ID from response
                checkout_request_id = response.get('CheckoutRequestID')
                
                # Create a Payment record
                Payment.objects.create(
                    order=order,
                    checkout_request_id=checkout_request_id,
                    status="PENDING",
                    raw_response=response
                )

                # Store checkout request ID for later verification
                request.session['checkout_request_id'] = checkout_request_id
                request.session['order_id'] = order.id
                
                logger.info(f"STK Push successful. CheckoutRequestID: {checkout_request_id}")
                
                # Clear cart after successful payment initiation
                cart = self.get_cart(request)
                cart.items.all().delete()
                cart.delete()
                
                # Check if this is an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'STK Push sent to your phone. Please enter your M-Pesa PIN.',
                        'checkout_request_id': checkout_request_id,
                        'order_number': order.order_number
                    })
                else:
                    messages.success(request, 'STK Push sent to your phone. Please enter your M-Pesa PIN.')
                    return redirect('order_confirmation', order_number=order.order_number)
            else:
                error_msg = response.get('ResponseDescription', 'Unknown error')
                logger.error(f"STK Push failed: {error_msg}")
                messages.error(request, f"M-Pesa payment failed: {error_msg}")
                order.delete()  # Clean up failed order
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f"M-Pesa payment failed: {error_msg}"
                    })
                else:
                    return self.get(request)
                    
        except Exception as e:
            logger.exception(f"M-Pesa payment initialization failed: {str(e)}")
            messages.error(request, f"Payment initialization failed: {str(e)}")
            order.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f"Payment initialization failed: {str(e)}"
                })
            else:
                return self.get(request)


# Keep the rest of your existing code (MpesaService, callback, etc.) unchanged
class MpesaService:
    def __init__(self):
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.business_shortcode = getattr(settings, 'MPESA_BUSINESS_SHORTCODE', '')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', '')
        self.environment = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
        
        logger.info(f"M-Pesa Service initialized - Environment: {self.environment}, Shortcode: {self.business_shortcode}")
        
        if not all([self.consumer_key, self.consumer_secret, self.business_shortcode, self.passkey]):
            logger.error("Missing M-Pesa configuration in settings")
            raise ValueError("M-Pesa configuration is incomplete. Check your settings.")
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
        
        logger.info(f"M-Pesa base URL: {self.base_url}")
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        logger.info("Requesting M-Pesa access token")
        
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            logger.debug(f"Token URL: {url}")
            
            # Create credentials string
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            logger.debug(f"Token request headers: {headers}")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Access token obtained successfully")
            logger.debug(f"Token response: {token_data}")
            
            return token_data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to get access token: {str(e)}")
            raise Exception(f"Failed to get access token: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error getting access token: {str(e)}")
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def generate_password(self):
        """Generate M-Pesa password"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        
        logger.debug(f"Generated timestamp: {timestamp}")
        logger.debug(f"Password string: {password_string}")
        
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push"""
        logger.info(f"Starting STK Push - Phone: {phone_number}, Amount: {amount}, Reference: {account_reference}")
        
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            logger.debug(f"STK Push URL: {url}")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': phone_number,
                'PartyB': self.business_shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': getattr(settings, 'MPESA_CALLBACK_URL', ''),
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }
            
            logger.info(f"STK Push payload: {payload}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"STK Push response: {response_data}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"STK Push request failed: {str(e)}")
            raise Exception(f"STK Push failed: {str(e)}")
        except Exception as e:
            logger.exception(f"STK Push unexpected error: {str(e)}")
            raise Exception(f"STK Push failed: {str(e)}")


@csrf_exempt
@require_POST
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    logger.info("M-Pesa callback received")
    logger.debug(f"Callback request body: {request.body}")
    
    try:
        callback_data = json.loads(request.body)
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_desc = stk_callback.get('ResultDesc')
        
        logger.info(f"Callback details - ResultCode: {result_code}, CheckoutRequestID: {checkout_request_id}, ResultDesc: {result_desc}")
        
        # Find Payment by checkout_request_id
        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
        if not payment:
            logger.error(f"No Payment found for CheckoutRequestID: {checkout_request_id}")
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
        order = payment.order
        
        if result_code == 0:  # Success
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            transaction_data = {item['Name']: item.get('Value') for item in callback_metadata}
            
            logger.info(f"Transaction data: {transaction_data}")
            
            # Update payment record
            payment.status = "SUCCESS"
            payment.mpesa_receipt = transaction_data.get('MpesaReceiptNumber')
            payment.phone_number = transaction_data.get('PhoneNumber')
            payment.transaction_date = str(transaction_data.get('TransactionDate'))
            payment.amount = transaction_data.get('Amount')
            payment.raw_response = callback_data
            payment.save()
            
            # Update order status
            order.payment_status = "paid"
            order.status = "confirmed"  # Change order status to confirmed
            order.save()
            
            # Store success info in session/cache for frontend polling
            # This allows the frontend to know when payment is complete
            from django.core.cache import cache
            cache.set(f"payment_status_{checkout_request_id}", {
                'status': 'SUCCESS',
                'order_number': order.order_number,
                'redirect_url': reverse('order_confirmation', kwargs={'order_number': order.order_number})
            }, timeout=300)  # 5 minutes
            
            logger.info(f"Payment completed - Receipt: {payment.mpesa_receipt}, Date: {payment.transaction_date}, Phone: {payment.phone_number}")
            logger.info(f"Order {order.order_number} confirmed and ready for redirect")
        
        else:  # Failed
            payment.status = "FAILED"
            payment.raw_response = callback_data
            payment.save()
            
            order.payment_status = "failed"
            order.status = "cancelled"  # Mark order as cancelled
            order.save()
            
            # Store failure info in cache
            from django.core.cache import cache
            cache.set(f"payment_status_{checkout_request_id}", {
                'status': 'FAILED',
                'message': result_desc,
                'redirect_url': reverse('checkout')
            }, timeout=300)
            
            logger.error(f"Payment failed - ResultCode: {result_code}, ResultDesc: {result_desc}")
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    
    except Exception as e:
        logger.exception(f"Error processing callback: {str(e)}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': f'Error processing callback: {str(e)}'})


# Keep the rest of your existing functions...
def apply_coupon(request):
    """Apply coupon code"""
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        if not coupon_code:
            messages.error(request, 'Please enter a coupon code.')
            return redirect('checkout')
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            
            if coupon.is_valid():
                cart = CheckoutView().get_cart(request)
                
                # Check minimum amount
                if coupon.minimum_amount and cart.total_price < coupon.minimum_amount:
                    messages.error(request, f'Minimum order amount of {coupon.minimum_amount} required for this coupon.')
                    return redirect('checkout')
                
                # Store coupon in session
                request.session['coupon_code'] = coupon_code
                messages.success(request, f'Coupon "{coupon_code}" applied successfully!')
            else:
                messages.error(request, 'This coupon is expired or not valid.')
        
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    
    return redirect('checkout')


def remove_coupon(request):
    """Remove applied coupon"""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.success(request, 'Coupon removed successfully.')
    
    return redirect('checkout')

def check_payment_status(request):
    """Check M-Pesa payment status via AJAX polling"""
    checkout_request_id = request.GET.get('checkout_request_id')
    logger.info(f"Checking payment status for CheckoutRequestID: {checkout_request_id}")
    
    if not checkout_request_id:
        return JsonResponse({'error': 'Checkout request ID required'}, status=400)
    
    try:
        # Check database first
        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
        
        if payment:
            if payment.status == "SUCCESS":
                # Clear any stored cart items and coupon from session
                if hasattr(request, 'session'):
                    if 'coupon_code' in request.session:
                        del request.session['coupon_code']
                
                return JsonResponse({
                    'status': 'SUCCESS',
                    'message': 'Payment completed successfully!',
                    'order_number': payment.order.order_number,
                    'redirect_url': reverse('order_confirmation', kwargs={'order_number': payment.order.order_number})
                })
            elif payment.status == "FAILED":
                return JsonResponse({
                    'status': 'FAILED',
                    'message': 'Payment failed. Please try again.',
                    'redirect_url': reverse('checkout')
                })
            else:
                # Still pending
                return JsonResponse({
                    'status': 'PENDING',
                    'message': 'Please complete the payment on your phone...'
                })
        
        # If no payment found, check cache (fallback)
        from django.core.cache import cache
        cached_status = cache.get(f"payment_status_{checkout_request_id}")
        
        if cached_status:
            return JsonResponse(cached_status)
        
        # Default pending response
        return JsonResponse({
            'status': 'PENDING',
            'message': 'Payment is being processed...'
        })
        
    except Exception as e:
        logger.exception(f"Error checking payment status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def order_confirmation(request, order_number):
    """Order confirmation page"""
    logger.info(f"Order confirmation for order: {order_number}")
    
    order = get_object_or_404(Order, order_number=order_number)
    
    # Verify user can access this order
    if request.user.is_authenticated and order.user != request.user:
        # Additional check for guest users or session validation could go here
        pass
    
    # Clear any remaining cart items and session data
    try:
        cart = CheckoutView().get_cart(request)
        if cart and cart.items.exists():
            cart.items.all().delete()
            cart.delete()
    except:
        pass  # Cart might already be cleared
    
    # Clear coupon from session
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    
    # Clear checkout session data
    session_keys_to_clear = ['checkout_request_id', 'order_id']
    for key in session_keys_to_clear:
        if key in request.session:
            del request.session[key]
    
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    
    return render(request, 'order_confirmation.html', context)

# views.py
from django.shortcuts import render
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Product, Category, Brand, ProductAttribute, ProductAttributeValue
import json
import re
from django.db.models import Min, Max
from django.db import models

import re
from django.db.models import (
    Q, Count, Avg, Case, When, Value, IntegerField,
    FloatField, F, ExpressionWrapper
)
from django.views.generic import ListView
from .models import Product, Category, Brand


class ProductSearchView(ListView):
    """Advanced product search view with fuzzy matching and filters"""
    model = Product
    template_name = 'products/search_results.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        category_id = self.request.GET.get('category')
        brand_id = self.request.GET.get('brand')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        sort_by = self.request.GET.get('sort', 'relevance')
        in_stock_only = self.request.GET.get('in_stock', False)

        # Start with active products
        queryset = Product.objects.filter(status='active').select_related('category', 'brand')

        # Apply search query if provided
        if query:
            queryset = self.apply_search_query(queryset, query)
        
        # Apply filters
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                category_ids = [category.id]
                subcategories = category.children.all()
                for subcat in subcategories:
                    category_ids.append(subcat.id)
                    category_ids.extend([c.id for c in subcat.children.all()])
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                pass

        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        if in_stock_only:
            queryset = queryset.filter(
                Q(track_inventory=False) |
                Q(track_inventory=True, stock_quantity__gt=0)
            )

        # Apply sorting
        queryset = self.apply_sorting(queryset, sort_by, query)

        return queryset.distinct()

    def apply_search_query(self, queryset, query):
        """Apply advanced search with multiple matching strategies"""
        exact_match = Q(name__iexact=query) | Q(sku__iexact=query)
        contains_match = (
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query)
        )

        words = query.split()
        word_queries = Q()
        for word in words:
            if len(word) > 2:
                word_queries |= (
                    Q(name__icontains=word) |
                    Q(description__icontains=word) |
                    Q(category__name__icontains=word) |
                    Q(brand__name__icontains=word)
                )

        fuzzy_queries = self.get_fuzzy_queries(query)

        search_filter = exact_match | contains_match | word_queries | fuzzy_queries
        return queryset.filter(search_filter)

    def get_fuzzy_queries(self, query):
        fuzzy_q = Q()
        variations = self.generate_query_variations(query)
        for variation in variations[:20]:
            fuzzy_q |= (
                Q(name__icontains=variation) |
                Q(description__icontains=variation) |
                Q(category__name__icontains=variation) |
                Q(brand__name__icontains=variation)
            )
        return fuzzy_q

    def generate_query_variations(self, query):
        variations = []
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        variations.append(clean_query)

        if len(query) <= 6:
            for i in range(len(query)):
                for char in 'abcdefghijklmnopqrstuvwxyz':
                    if char != query[i].lower():
                        variation = query[:i] + char + query[i+1:]
                        variations.append(variation)

        substitutions = {
            'phone': ['fone', 'phon'],
            'mobile': ['mobil', 'moble'],
            'laptop': ['lptop', 'labtop'],
            'computer': ['computr', 'compter'],
            'camera': ['camra', 'camer'],
            'watch': ['wach', 'wtch'],
            'headphone': ['headfone', 'hedphone'],
            'speaker': ['speakr', 'speker'],
        }

        query_lower = query.lower()
        for correct, typos in substitutions.items():
            if correct in query_lower:
                for typo in typos:
                    variations.append(query_lower.replace(correct, typo))
            for typo in typos:
                if typo in query_lower:
                    variations.append(query_lower.replace(typo, correct))

        return list(set(variations))

    def apply_sorting(self, queryset, sort_by, query=None):
        """Apply sorting to queryset without ambiguous 'name' errors"""
        if sort_by == 'price_low':
            return queryset.order_by('price', 'id')
        elif sort_by == 'price_high':
            return queryset.order_by('-price', 'id')
        elif sort_by == 'name_asc':
            return queryset.order_by('name')  # safe: Product.name
        elif sort_by == 'name_desc':
            return queryset.order_by('-name')
        elif sort_by == 'newest':
            return queryset.order_by('-created_at')
        elif sort_by == 'rating':
            return queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', '-created_at')
        elif sort_by == 'popular':
            return queryset.order_by('-sales_count', '-view_count')
        else:  # relevance
            if query:
                return queryset.annotate(
                    relevance_score=Case(
                        When(name__iexact=query, then=Value(100)),
                        When(name__icontains=query, then=Value(80)),
                        When(description__icontains=query, then=Value(60)),
                        default=Value(40),
                        output_field=IntegerField()
                    ) +
                    ExpressionWrapper(F('sales_count') * 0.1, output_field=FloatField()) +
                    ExpressionWrapper(F('view_count') * 0.05, output_field=FloatField())
                ).order_by('-relevance_score', '-created_at')
            else:
                return queryset.order_by('-is_featured', '-sales_count', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        queryset = self.get_queryset()

        context.update({
            'search_query': query,
            'total_products': queryset.count(),
            'categories': self.get_filtered_categories(),
            'brands': self.get_filtered_brands(),
            'price_range': self.get_price_range(),
            'current_filters': self.get_current_filters(),
            'suggestions': self.get_search_suggestions(query) if query else [],
            'related_searches': self.get_related_searches(query) if query else [],
        })
        return context

    def get_filtered_categories(self):
        queryset = self.get_queryset()
        category_ids = queryset.values_list('category_id', flat=True).distinct()
        return Category.objects.filter(
            id__in=category_ids
        ).annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0).order_by('name')

    def get_filtered_brands(self):
        queryset = self.get_queryset()
        brand_ids = queryset.values_list('brand_id', flat=True).distinct()
        return Brand.objects.filter(
            id__in=brand_ids
        ).annotate(
            product_count=Count('product')
        ).filter(product_count__gt=0).order_by('name')

    def get_price_range(self):
        queryset = self.get_queryset()
        if queryset.exists():
            prices = queryset.aggregate(
                min_price=models.Min('price'),
                max_price=models.Max('price')
            )
            return prices
        return {'min_price': 0, 'max_price': 0}

    def get_current_filters(self):
        return {
            'category': self.request.GET.get('category'),
            'brand': self.request.GET.get('brand'),
            'min_price': self.request.GET.get('min_price'),
            'max_price': self.request.GET.get('max_price'),
            'sort': self.request.GET.get('sort', 'relevance'),
            'in_stock': self.request.GET.get('in_stock', False),
        }

    def get_search_suggestions(self, query):
        suggestions = []

        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:5]

        for category in categories:
            suggestions.append({
                'type': 'category',
                'text': category.name,
                'url': f'/search/?category={category.id}',
                'count': category.products.filter(status='active').count()
            })

        brands = Brand.objects.filter(name__icontains=query)[:3]
        for brand in brands:
            suggestions.append({
                'type': 'brand',
                'text': brand.name,
                'url': f'/search/?brand={brand.id}',
                'count': brand.product.filter(status='active').count()
            })

        products = Product.objects.filter(
            Q(name__icontains=query) & Q(status='active')
        ).distinct()[:5]

        for product in products:
            suggestions.append({
                'type': 'product',
                'text': product.name,
                'url': product.get_absolute_url(),
                'price': product.price,
                'image': product.images.first().image.url if product.images.exists() else None
            })

        return suggestions

    def get_related_searches(self, query):
        related = []
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values_list('name', flat=True)[:10]

        words = set()
        for product_name in products:
            product_words = re.findall(r'\w+', product_name.lower())
            words.update([word for word in product_words if len(word) > 3])

        query_words = set(re.findall(r'\w+', query.lower()))
        related_words = words - query_words

        for word in list(related_words)[:5]:
            related.append({
                'text': f"{query} {word}",
                'url': f'/search/?q={query}+{word}'
            })
        return related



def search_autocomplete(request):
    """AJAX endpoint for search autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Product suggestions
    products = Product.objects.filter(
        Q(name__icontains=query) & Q(status='active')
    ).select_related('category', 'brand')[:8]
    
    for product in products:
        suggestions.append({
            'type': 'product',
            'title': product.name,
            'category': product.category.name,
            'price': str(product.price),
            'url': product.get_absolute_url(),
            'image': product.images.first().image.url if product.images.exists() else '',
            'in_stock': product.is_in_stock,
        })
    
    # Category suggestions
    categories = Category.objects.filter(
        Q(name__icontains=query) & Q(is_active=True)
    )[:4]
    
    for category in categories:
        suggestions.append({
            'type': 'category',
            'title': category.name,
            'count': category.products.filter(status='active').count(),
            'url': f'/search/?category={category.id}',
        })
    
    # Brand suggestions
    brands = Brand.objects.filter(
        Q(name__icontains=query) & Q(is_active=True)
    )[:3]
    
    for brand in brands:
        suggestions.append({
            'type': 'brand',
            'title': brand.name,
            'count': brand.product.filter(status='active').count(),
            'url': f'/search/?brand={brand.id}',
        })
    
    return JsonResponse({'suggestions': suggestions})


def search_filters(request):
    """AJAX endpoint for getting filter options based on search"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    
    # Get base queryset
    queryset = Product.objects.filter(status='active')
    
    if query:
        # Apply same search logic as main view
        search_view = ProductSearchView()
        queryset = search_view.apply_search_query(queryset, query)
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    # Get filter options
    categories = Category.objects.filter(
        products__in=queryset
    ).annotate(
        product_count=Count('products', filter=Q(products__in=queryset))
    ).filter(product_count__gt=0).values('id', 'name', 'product_count')
    
    brands = Brand.objects.filter(
        product__in=queryset
    ).annotate(
        product_count=Count('product', filter=Q(product__in=queryset))
    ).filter(product_count__gt=0).values('id', 'name', 'product_count')
    
    # Get price range
    price_range = queryset.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    return JsonResponse({
        'categories': list(categories),
        'brands': list(brands),
        'price_range': price_range,
        'total_products': queryset.count()
    })


# Additional views and helpers for search functionality

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, F
from django.core.cache import cache
from .models import Product, Category, Brand, ProductView
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def search_analytics(request):
    """Track search analytics"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({'status': 'error', 'message': 'No query provided'})
        
        # Log search query for analytics
        logger.info(f"Search query: {query}")
        
        # You can store search analytics in database
        # SearchAnalytics.objects.create(
        #     query=query,
        #     user=request.user if request.user.is_authenticated else None,
        #     session_key=request.session.session_key,
        #     ip_address=get_client_ip(request),
        #     timestamp=timezone.now()
        # )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error tracking search analytics: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to track analytics'})


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def track_product_view(request, product):
    """Track product views for analytics"""
    try:
        ProductView.objects.update_or_create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            defaults={
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        
        # Update product view count
        Product.objects.filter(id=product.id).update(view_count=F('view_count') + 1)
        
    except Exception as e:
        logger.error(f"Error tracking product view: {e}")


def get_trending_searches():
    """Get trending search terms (implement based on your analytics data)"""
    # This is a placeholder - implement based on your search analytics model
    trending = [
        'smartphone', 'laptop', 'wireless earbuds', 'smartwatch', 
        'gaming chair', 'monitor', 'keyboard', 'mouse', 'webcam'
    ]
    return trending


def get_popular_products_by_category(category_id, limit=10):
    """Get popular products in a category"""
    cache_key = f'popular_products_category_{category_id}_{limit}'
    products = cache.get(cache_key)
    
    if not products:
        products = Product.objects.filter(
            category_id=category_id,
            status='active'
        ).order_by('-sales_count', '-view_count')[:limit]
        
        # Cache for 1 hour
        cache.set(cache_key, products, 3600)
    
    return products


def get_search_suggestions_for_query(query):
    """Get enhanced search suggestions"""
    suggestions = []
    
    # Product name matches
    products = Product.objects.filter(
        Q(name__icontains=query) & Q(status='active')
    ).select_related('category', 'brand')[:5]
    
    for product in products:
        suggestions.append({
            'type': 'product',
            'title': product.name,
            'category': product.category.name,
            'brand': product.brand.name if product.brand else '',
            'price': str(product.price),
            'url': product.get_absolute_url(),
            'image': product.images.first().image.url if product.images.exists() else '',
            'in_stock': product.is_in_stock,
        })
    
    # Category matches
    categories = Category.objects.filter(
        Q(name__icontains=query) & Q(is_active=True)
    )[:3]
    
    for category in categories:
        suggestions.append({
            'type': 'category',
            'title': category.name,
            'count': category.products.filter(status='active').count(),
            'url': f'/search/?category={category.id}',
        })
    
    # Brand matches
    brands = Brand.objects.filter(
        Q(name__icontains=query) & Q(is_active=True)
    )[:3]
    
    for brand in brands:
        suggestions.append({
            'type': 'brand',
            'title': brand.name,
            'count': brand.product.filter(status='active').count(),
            'url': f'/search/?brand={brand.id}',
        })
    
    return suggestions


class SearchRecommendations:
    """Class to handle search recommendations and related products"""
    
    @staticmethod
    def get_related_products(product, limit=6):
        """Get products related to the current product"""
        # Same category products
        related = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id)
        
        # If same brand, prioritize those
        if product.brand:
            related = related.extra(
                select={'same_brand': f"CASE WHEN brand_id = {product.brand.id} THEN 1 ELSE 0 END"}
            ).order_by('-same_brand', '-sales_count', '-view_count')
        else:
            related = related.order_by('-sales_count', '-view_count')
        
        return related[:limit]
    
    @staticmethod
    def get_frequently_bought_together(product, limit=4):
        """Get products frequently bought together"""
        # This would require order analytics - placeholder implementation
        return Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).order_by('-sales_count')[:limit]
    
    @staticmethod
    def get_customers_also_viewed(product, limit=6):
        """Get products that customers also viewed"""
        # This would require view analytics - placeholder implementation
        return Product.objects.filter(
            Q(category=product.category) | Q(brand=product.brand),
            status='active'
        ).exclude(id=product.id).order_by('-view_count')[:limit]


# Context processor for search functionality
def search_context_processor(request):
    """Add search-related context to all templates"""
    context = {
        'search_categories': Category.objects.filter(
            is_active=True, 
            parent=None  # Only top-level categories
        ).order_by('name')[:10],
        'trending_searches': get_trending_searches()[:8],
    }
    
    # Add current search query if exists
    if request.GET.get('q'):
        context['current_search'] = request.GET.get('q')
    
    return context


# Utility functions for search
def normalize_search_query(query):
    """Normalize search query for better matching"""
    import re
    
    # Remove special characters
    query = re.sub(r'[^\w\s]', '', query)
    
    # Convert to lowercase
    query = query.lower().strip()
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query)
    
    return query


def get_search_filters_context(request, queryset):
    """Get filter context for search results"""
    # Get price range
    price_range = queryset.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    # Get available categories
    categories = Category.objects.filter(
        products__in=queryset
    ).annotate(
        product_count=Count('products', filter=Q(products__in=queryset))
    ).filter(product_count__gt=0).order_by('name')
    
    # Get available brands
    brands = Brand.objects.filter(
        product__in=queryset
    ).annotate(
        product_count=Count('product', filter=Q(product__in=queryset))
    ).filter(product_count__gt=0).order_by('name')
    
    return {
        'price_range': price_range,
        'filter_categories': categories,
        'filter_brands': brands,
    }


# SEO helpers for search pages
def generate_search_meta_tags(query, results_count):
    """Generate meta tags for search pages"""
    if not query:
        return {
            'meta_title': 'Search Products',
            'meta_description': 'Search through our wide range of products to find exactly what you need.',
        }
    
    return {
        'meta_title': f'Search Results for "{query}" - {results_count} Products Found',
        'meta_description': f'Found {results_count} products matching "{query}". Browse and compare prices, read reviews, and shop with confidence.',
    }


# Advanced search features
class AdvancedSearchFeatures:
    """Advanced search features like spell correction, etc."""
    
    @staticmethod
    def get_spell_suggestions(query):
        """Get spelling suggestions for search query"""
        # This is a placeholder - you could integrate with a spell-checking service
        # or implement a simple edit distance algorithm
        
        common_typos = {
            'phon': 'phone',
            'lptop': 'laptop',
            'computr': 'computer',
            'camra': 'camera',
            'hedphones': 'headphones',
        }
        
        words = query.lower().split()
        corrected_words = []
        has_corrections = False
        
        for word in words:
            if word in common_typos:
                corrected_words.append(common_typos[word])
                has_corrections = True
            else:
                corrected_words.append(word)
        
        if has_corrections:
            return ' '.join(corrected_words)
        
        return None
    
    @staticmethod
    def get_category_suggestions(query):
        """Get category suggestions based on query"""
        # Look for category keywords in query
        category_keywords = {
            'phone': ['mobile', 'smartphone', 'cell'],
            'laptop': ['computer', 'notebook'],
            'accessories': ['case', 'cover', 'charger', 'cable'],
            'audio': ['headphones', 'speakers', 'earbuds'],
            'gaming': ['game', 'console', 'controller'],
        }
        
        query_lower = query.lower()
        suggestions = []
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords + [category]):
                try:
                    cat = Category.objects.get(name__icontains=category, is_active=True)
                    suggestions.append(cat)
                except Category.DoesNotExist:
                    pass
        
        return suggestions
    


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Order, Address, SiteSetting
from .forms import UserProfileForm, AddressForm, ContactForm
from django.db.models import Q


@login_required
def account_profile(request):
    """User account profile view"""
    user = request.user
    addresses = user.addresses.all()
    
    # Get user statistics
    total_orders = user.orders.count()
    pending_orders = user.orders.filter(status='pending').count()
    delivered_orders = user.orders.filter(status='delivered').count()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('account_profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'user': user,
        'form': form,
        'addresses': addresses,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'account/profile.html', context)


@login_required
def my_orders(request):
    """User orders listing view"""
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    orders = user.orders.all()
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(items__product__name__icontains=search_query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_orders = paginator.get_page(page_number)
    
    # Order status choices for filter dropdown
    status_choices = Order.ORDER_STATUS
    
    context = {
        'orders': page_orders,
        'status_choices': status_choices,
        'current_status': status_filter,
        'search_query': search_query,
        'total_orders': orders.count(),
    }
    return render(request, 'account/orders.html', context)


@login_required
def order_detail(request, order_number):
    """Individual order detail view"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'account/order_detail.html', context)


def contact_us(request):
    """Contact us view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the contact form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email to admin
            try:
                full_message = f"""
                Name: {name}
                Email: {email}
                Subject: {subject}
                
                Message:
                {message}
                """
                
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=full_message,
                    from_email=email,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message. We will get back to you soon!')
                return redirect('contact_us')
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
    else:
        # Pre-fill form if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
            }
        form = ContactForm(initial=initial_data)
    
    # Get contact information from site settings
    try:
        contact_email = SiteSetting.objects.get(key='contact_email').value
    except SiteSetting.DoesNotExist:
        contact_email = 'support@galiostores.com'
    
    try:
        contact_phone = SiteSetting.objects.get(key='contact_phone').value
    except SiteSetting.DoesNotExist:
        contact_phone = '+254 762 625 728'
    
    try:
        contact_address = SiteSetting.objects.get(key='contact_address').value
    except SiteSetting.DoesNotExist:
        contact_address = 'Nairobi, Kenya'
    
    context = {
        'form': form,
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'contact_address': contact_address,
    }
    return render(request, 'account/contact_us.html', context)


@login_required
def add_address(request):
    """Add new address view"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, remove default from other addresses of same type
            if address.is_default:
                Address.objects.filter(
                    user=request.user,
                    address_type=address.address_type,
                    is_default=True
                ).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('account_profile')
    else:
        form = AddressForm()
    
    context = {'form': form}
    return render(request, 'account/add_address.html', context)


@login_required
def edit_address(request, address_id):
    """Edit existing address view"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # If this is set as default, remove default from other addresses of same type
            if address.is_default:
                Address.objects.filter(
                    user=request.user,
                    address_type=address.address_type,
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('account_profile')
    else:
        form = AddressForm(instance=address)
    
    context = {'form': form, 'address': address}
    return render(request, 'account/edit_address.html', context)


@login_required
@require_POST
def delete_address(request, address_id):
    """Delete address via AJAX"""
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True, 'message': 'Address deleted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error deleting address.'})


@login_required
@require_POST
def cancel_order(request, order_number):
    """Cancel order if allowed"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Only allow cancellation for pending orders
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        
        # Restore stock quantities
        for item in order.items.all():
            if item.product.track_inventory:
                item.product.stock_quantity += item.quantity
                item.product.save()
        
        messages.success(request, f'Order {order.order_number} has been cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('my_orders')