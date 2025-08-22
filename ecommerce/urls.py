from django.urls import path
from . import views
urlpatterns = [
    path('', views.index , name="index"),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/', views.product_list, name='product_list'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # Category URLs
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('categories/', views.all_categories, name='all_categories'),
    
    # Brand URLs
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),
    path('brands/', views.all_brands, name='all_brands'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),

    # Checkout URLs
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),

    # Main search page
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path('autocomplete/', views.search_autocomplete, name='autocomplete'),
    path('filters/', views.search_filters, name='filters'),
    path('analytics/', views.search_analytics, name='analytics'),

]
