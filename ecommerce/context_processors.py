# context_processor.py
from .models import Category, Brand


def global_context(request):
    """
    Context processor to make categories and brands available globally
    """
    # Get all active categories ordered by sort_order and name
    categories = Category.objects.filter(is_active=True).select_related('parent')
    
    # Get all active brands
    brands = Brand.objects.filter(is_active=True)
    
    # Organize categories hierarchically
    parent_categories = categories.filter(parent__isnull=True)
    child_categories = categories.filter(parent__isnull=False)
    
    # Create a dictionary to group children by parent
    categories_with_children = {}
    for parent in parent_categories:
        children = child_categories.filter(parent=parent)
        if children.exists():  # Only add parents that have children
            categories_with_children[parent] = children
    
    return {
        'all_categories': categories,
        'parent_categories': parent_categories,
        'categories_with_children': categories_with_children,
        'all_brands': brands,
    }

from .models import Cart, CartItem

def cart_context(request):
    context = {}
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    cart_items = CartItem.objects.filter(cart=cart).select_related('product', 'variant')
    cart_items_count = cart_items.count()
    
    # Calculate totals
    cart_subtotal = sum(item.total_price for item in cart_items)
    shipping_cost = 0  # You can implement your shipping logic here
    coupon_discount = 0  # Will be set when coupon is applied
    cart_total = cart_subtotal + shipping_cost - coupon_discount
    
    context.update({
        'cart': cart,
        'cart_items': cart_items,
        'cart_items_count': cart_items_count,
        'cart_subtotal': cart_subtotal,
        'shipping_cost': shipping_cost,
        'coupon_discount': coupon_discount,
        'cart_total': cart_total,
    })
    
    return context