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