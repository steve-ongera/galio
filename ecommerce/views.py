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


@csrf_protect
def login_view(request):
    """Handle user login"""
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('index')  # Change to your desired redirect URL
    
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
    
    return render(request, 'auth/login.html')


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
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
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
                password=make_password(password)
            )
            
            # Auto-login after registration
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome {first_name}! Your account has been created successfully.')
                return redirect('dashboard')  # Change to your desired redirect URL
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


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant_id')  # If you have variants
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    # Check if item already in cart
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

from .models import Cart, CartItem, Order, OrderItem, Address, Coupon, User
from .forms import CheckoutForm, BillingAddressForm, ShippingAddressForm


class CheckoutView(View):
    template_name = 'checkout.html'
    
    def get(self, request):
        # Get or create cart
        cart = self.get_cart(request)
        
        if not cart or not cart.items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart')
        
        # Get user addresses if authenticated
        addresses = []
        if request.user.is_authenticated:
            addresses = Address.objects.filter(user=request.user)
        
        # Initialize forms
        billing_form = BillingAddressForm()
        shipping_form = ShippingAddressForm()
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'billing_form': billing_form,
            'shipping_form': shipping_form,
            'addresses': addresses,
            'subtotal': cart.total_price,
            'shipping_cost': self.calculate_shipping(cart),
            'tax_amount': self.calculate_tax(cart),
            'total_amount': self.calculate_total(cart),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        cart = self.get_cart(request)
        
        if not cart or not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
        
        billing_form = BillingAddressForm(request.POST, prefix='billing')
        
        # Check if shipping to different address
        ship_to_different = request.POST.get('ship_to_different') == 'on'
        shipping_form = ShippingAddressForm(request.POST, prefix='shipping') if ship_to_different else None
        
        if billing_form.is_valid() and (not shipping_form or shipping_form.is_valid()):
            try:
                with transaction.atomic():
                    # Create or get user
                    user = self.get_or_create_user(request, billing_form.cleaned_data)
                    
                    # Calculate amounts
                    subtotal = cart.total_price
                    shipping_cost = self.calculate_shipping(cart)
                    tax_amount = self.calculate_tax(cart)
                    discount_amount = self.apply_coupon(request, subtotal)
                    total_amount = subtotal + shipping_cost + tax_amount - discount_amount
                    
                    # Create order
                    order = Order.objects.create(
                        user=user,
                        subtotal=subtotal,
                        shipping_amount=shipping_cost,
                        tax_amount=tax_amount,
                        discount_amount=discount_amount,
                        total_amount=total_amount,
                        billing_address=self.format_address(billing_form.cleaned_data),
                        shipping_address=self.format_address(shipping_form.cleaned_data if shipping_form else billing_form.cleaned_data),
                        payment_method=request.POST.get('paymentmethod', 'mpesa'),
                    )
                    
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
                    
                    # Handle payment
                    payment_method = request.POST.get('paymentmethod', 'mpesa')
                    
                    if payment_method == 'mpesa':
                        phone_number = self.clean_phone_number(billing_form.cleaned_data.get('phone'))
                        if phone_number:
                            return self.initiate_mpesa_payment(request, order, phone_number)
                        else:
                            messages.error(request, 'Valid phone number is required for M-Pesa payment.')
                            return self.get(request)
                    else:
                        # Handle other payment methods
                        return redirect('order_confirmation', order_number=order.order_number)
                        
            except Exception as e:
                messages.error(request, f'An error occurred while processing your order: {str(e)}')
                return self.get(request)
        else:
            messages.error(request, 'Please correct the errors below.')
            
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'billing_form': billing_form,
            'shipping_form': shipping_form,
            'subtotal': cart.total_price,
            'shipping_cost': self.calculate_shipping(cart),
            'tax_amount': self.calculate_tax(cart),
            'total_amount': self.calculate_total(cart),
        }
        
        return render(request, self.template_name, context)
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key or request.session._get_or_create_session_key()
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart
    
    def get_or_create_user(self, request, form_data):
        if request.user.is_authenticated:
            return request.user
        
        # Check if user wants to create account
        if request.POST.get('create_pwd'):
            email = form_data.get('email')
            password = request.POST.get('pwd')
            
            if User.objects.filter(email=email).exists():
                messages.info(request, 'An account with this email already exists.')
                return User.objects.get(email=email)
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=form_data.get('first_name', ''),
                last_name=form_data.get('last_name', ''),
                phone=form_data.get('phone', '')
            )
            return user
        
        # For guest checkout, you might want to create a guest user or handle differently
        # For now, we'll require authentication
        return request.user
    
    def format_address(self, address_data):
        return f"{address_data.get('first_name', '')} {address_data.get('last_name', '')}\n" \
               f"{address_data.get('company', '')}\n" \
               f"{address_data.get('address_line_1', '')}\n" \
               f"{address_data.get('address_line_2', '')}\n" \
               f"{address_data.get('city', '')}, {address_data.get('state', '')} {address_data.get('postal_code', '')}\n" \
               f"{address_data.get('country', '')}\n" \
               f"Phone: {address_data.get('phone', '')}"
    
    def calculate_shipping(self, cart):
        # Implement your shipping calculation logic
        return Decimal('70.00')  # Flat rate for now
    
    def calculate_tax(self, cart):
        # Implement your tax calculation logic
        tax_rate = Decimal('0.16')  # 16% VAT in Kenya
        return cart.total_price * tax_rate
    
    def calculate_total(self, cart):
        subtotal = cart.total_price
        shipping = self.calculate_shipping(cart)
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
        # This is a simplified version, you should integrate with session
        return Decimal('0.00')
    
    def clean_phone_number(self, phone):
        """Clean and format phone number for M-Pesa"""
        if not phone:
            return None
        
        # Remove all non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Handle Kenyan phone numbers
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+254'):
            phone = phone[1:]
        elif phone.startswith('254'):
            pass
        elif len(phone) == 9:
            phone = '254' + phone
        
        # Validate length
        if len(phone) == 12 and phone.startswith('254'):
            return phone
        
        return None
    
    def initiate_mpesa_payment(self, request, order, phone_number):
        """Initiate M-Pesa STK Push"""
        try:
            mpesa_service = MpesaService()
            response = mpesa_service.stk_push(
                phone_number=phone_number,
                amount=int(order.total_amount),
                account_reference=order.order_number,
                transaction_desc=f"Payment for order {order.order_number}"
            )
            
            if response.get('ResponseCode') == '0':
                # Store checkout request ID for later verification
                request.session['checkout_request_id'] = response.get('CheckoutRequestID')
                request.session['order_id'] = order.id
                
                return JsonResponse({
                    'success': True,
                    'message': 'STK Push sent to your phone. Please enter your M-Pesa PIN.',
                    'checkout_request_id': response.get('CheckoutRequestID')
                })
            else:
                messages.error(request, f"M-Pesa payment failed: {response.get('ResponseDescription', 'Unknown error')}")
                order.delete()  # Clean up failed order
                return self.get(request)
                
        except Exception as e:
            messages.error(request, f"Payment initialization failed: {str(e)}")
            order.delete()
            return self.get(request)


class MpesaService:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.environment = settings.MPESA_ENVIRONMENT  # 'sandbox' or 'production'
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            # Create credentials string
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json().get('access_token')
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def generate_password(self):
        """Generate M-Pesa password"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push"""
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
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
                'CallBackURL': settings.MPESA_CALLBACK_URL,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"STK Push failed: {str(e)}")


@csrf_exempt
@require_POST
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    try:
        callback_data = json.loads(request.body)
        
        # Extract relevant data
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        if result_code == 0:  # Success
            # Extract transaction details
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            transaction_data = {}
            
            for item in callback_metadata:
                name = item.get('Name')
                value = item.get('Value')
                transaction_data[name] = value
            
            # Find the order using checkout_request_id
            # You might need to store this mapping in a model or cache
            try:
                # Update order status
                # This is a simplified approach - you should implement proper order tracking
                mpesa_receipt_number = transaction_data.get('MpesaReceiptNumber')
                transaction_date = transaction_data.get('TransactionDate')
                phone_number = transaction_data.get('PhoneNumber')
                
                # Update order payment status
                # You'll need to implement a way to link checkout_request_id to order
                # For now, this is a placeholder
                
                return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
                
            except Exception as e:
                return JsonResponse({'ResultCode': 1, 'ResultDesc': f'Failed to process: {str(e)}'})
        else:
            # Payment failed
            result_desc = stk_callback.get('ResultDesc')
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
            
    except Exception as e:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': f'Error processing callback: {str(e)}'})


@login_required
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
                    messages.error(request, f'Minimum order amount of ${coupon.minimum_amount} required for this coupon.')
                    return redirect('checkout')
                
                # Store coupon in session
                request.session['coupon_code'] = coupon_code
                messages.success(request, f'Coupon "{coupon_code}" applied successfully!')
            else:
                messages.error(request, 'This coupon is expired or not valid.')
        
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    
    return redirect('checkout')


@login_required
def remove_coupon(request):
    """Remove applied coupon"""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.success(request, 'Coupon removed successfully.')
    
    return redirect('checkout')


def check_payment_status(request):
    """Check M-Pesa payment status"""
    checkout_request_id = request.GET.get('checkout_request_id')
    
    if not checkout_request_id:
        return JsonResponse({'error': 'Checkout request ID required'}, status=400)
    
    try:
        mpesa_service = MpesaService()
        # Implement query status if needed
        # For now, return a placeholder response
        return JsonResponse({
            'status': 'pending',
            'message': 'Payment is being processed...'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Clear cart after successful order
    cart = CheckoutView().get_cart(request)
    if cart:
        cart.items.all().delete()
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
    
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    
    return render(request, 'order_confirmation.html', context)