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
from decimal import Decimal

def cart_context(request):
    """
    Context processor to make cart data available across all templates
    """
    context = {
        'cart_items_count': 0,
        'cart_items': [],
        'cart_subtotal': Decimal('0.00'),
        'shipping_cost': Decimal('0.00'),
        'coupon_discount': Decimal('0.00'),
        'cart_total': Decimal('0.00'),
        'cart': None,
    }
    
    try:
        cart = None
        
        if request.user.is_authenticated:
            # Only for authenticated users
            try:
                cart = Cart.objects.get(user=request.user)
                print(f"Found existing cart for user {request.user.email}: Cart ID {cart.id}")
            except Cart.DoesNotExist:
                print(f"No cart found for user {request.user.email}")
                return context
        else:
            # For anonymous users, return empty context
            print("Anonymous user - no cart data shown")
            return context
        
        if cart:
            # Get cart items using the correct related name 'items'
            cart_items = cart.items.select_related('product', 'variant').all()
            cart_items_count = cart_items.count()
            
            print(f"Cart ID {cart.id} has {cart_items_count} items")
            
            # Calculate totals using the model's total_price property
            cart_subtotal = Decimal('0.00')
            for item in cart_items:
                item_total = item.total_price  # This uses the property from your model
                cart_subtotal += item_total
                print(f"Item: {item.product.name}, Qty: {item.quantity}, Unit Price: {item.unit_price}, Total: {item_total}")
            
            # Alternative: Use the cart's built-in total_price property
            # cart_subtotal = cart.total_price
            
            shipping_cost = Decimal('0.00')  # Implement shipping logic
            coupon_discount = Decimal('0.00')  # Implement coupon logic
            cart_total = cart_subtotal + shipping_cost - coupon_discount
            
            # Update context
            context.update({
                'cart': cart,
                'cart_items': cart_items,
                'cart_items_count': cart_items_count,
                'cart_subtotal': cart_subtotal,
                'shipping_cost': shipping_cost,
                'coupon_discount': coupon_discount,
                'cart_total': cart_total,
            })
            
            print(f"Final context - Count: {cart_items_count}, Subtotal: {cart_subtotal}, Total: {cart_total}")
        else:
            print("No cart found")
    
    except Exception as e:
        print(f"Error in cart_context: {e}")
        import traceback
        print(traceback.format_exc())
    
    return context