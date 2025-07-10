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