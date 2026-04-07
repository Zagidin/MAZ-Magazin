from io import BytesIO

import qrcode
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from store.models import (
    Order,
    OrderPackage,
    Product,
    Category,
    EquipmentType,
)


def index(request):
    """
    Главная страница
    """
    products = Product.objects.filter(is_active=True, quantity__gt=0)[:12]
    categories = Category.objects.all()[:5]
    equipment_types = EquipmentType.objects.all()[:5]

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    last_order = None
    last_order_uuid = request.session.get('last_order_uuid')
    if last_order_uuid:
        try:
            import uuid
            last_order = Order.objects.get(uuid=uuid.UUID(last_order_uuid))
        except (Order.DoesNotExist, ValueError):
            pass

    context = {
        'products': products,
        'categories': categories,
        'equipment_types': equipment_types,
        'cart_count': cart_count,
        'last_order': last_order,
    }
    return render(request, 'store/index.html', context)


def catalog(request):
    """
    Каталог товаров
    """
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    equipment_types = EquipmentType.objects.all()

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    equipment = request.GET.get('equipment', '')
    in_stock = request.GET.get('in_stock', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(article__icontains=query)
        )

    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    if equipment:
        products = products.filter(equipment_type__name__iexact=equipment)

    if in_stock:
        products = products.filter(quantity__gt=0)

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'products': products,
        'categories': categories,
        'equipment_types': equipment_types,
        'query': query,
        'category_id': int(category_id) if category_id and category_id.isdigit() else None,
        'equipment': equipment,
        'in_stock': bool(in_stock),
        'cart_count': cart_count,
    }
    return render(request, 'store/catalog.html', context)


def product_detail(request, pk):
    """
    Детали товара + подбор похожих
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)

    similar = Product.objects.filter(
        category=product.category,
        equipment_type=product.equipment_type,
        is_active=True
    ).exclude(id=product.id)

    if similar.count() < 4:
        extra = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).exclude(id__in=similar.values('id'))

        similar = list(similar) + list(extra)

    related_products = similar[:8]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def order_qr_image(request, uuid):
    """
    Генерация QR-кода для заказа
    """
    order = get_object_or_404(Order, uuid=uuid)
    qr = qrcode.make(order.get_qr_data())

    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')


def package_qr_image(request, uuid):
    """
    Генерация QR-кода для пакета
    """
    package = get_object_or_404(OrderPackage, uuid=uuid)
    qr = qrcode.make(package.get_qr_data())

    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')