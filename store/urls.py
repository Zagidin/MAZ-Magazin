from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Главные страницы
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),

    # Корзина и оформление
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Заказы пользователя
    path('order/<uuid:uuid>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Авторизация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # QR-коды
    path('api/qr/order/<uuid:uuid>/', views.order_qr_image, name='order_qr'),
    path('api/qr/package/<uuid:uuid>/', views.package_qr_image, name='package_qr'),

    # API корзины
    path('api/cart/count/', views.cart_count_api, name='cart_count_api'),
    path('api/cart/items/', views.cart_items_api, name='cart_items_api'),
    path('api/cart/add/<int:product_id>/', views.cart_add_api, name='cart_add_api'),
    path('api/cart/update/<int:product_id>/', views.cart_update_api, name='cart_update_api'),
    path('api/cart/remove/<int:product_id>/', views.cart_remove_api, name='cart_remove_api'),

    # API товаров и заказов
    path('api/product/<int:pk>/', views.product_api, name='product_api'),
    path('api/order/<uuid:uuid>/', views.order_api, name='order_api'),

    # API обновлений
    path('api/order/<uuid:order_uuid>/updates/', views.order_updates_api, name='order_updates_api'),
    path('api/orders/updates/', views.orders_updates_api, name='orders_updates_api'),

    # API сканера / поиска
    path('api/scan-verify/', views.scan_verify, name='scan_verify'),
    path('api/product-by-article/', views.product_by_article_api, name='product_by_article_api'),
    path('api/order/<uuid:order_uuid>/add-item/', views.order_add_item_api, name='order_add_item_api'),

    # Панель продавца
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/order/<uuid:uuid>/', views.seller_order_detail, name='seller_order_detail'),
    path('seller/order/<uuid:uuid>/pack/', views.seller_pack_order, name='seller_pack_order'),
    path('seller/verify/', views.seller_verify_qr, name='seller_verify_qr'),
    path('seller/print-qr/<uuid:uuid>/', views.seller_print_qr, name='seller_print_qr'),

    # Сборка заказа
    path('seller/assemble/<uuid:order_uuid>/', views.seller_assemble, name='seller_assemble'),
    path('seller/assemble/<uuid:order_uuid>/finish/', views.seller_finish_assembly, name='seller_finish_assembly'),
]