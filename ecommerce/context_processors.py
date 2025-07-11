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