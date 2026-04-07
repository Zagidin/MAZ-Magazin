import base64
from io import BytesIO

import qrcode
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from store.models import Order


@staff_member_required
def seller_dashboard(request):
    """
    Панель продавца — умная фильтрация заказов
    """
    today = timezone.now().date()

    orders = Order.objects.filter(
        Q(status='new') | Q(created_at__date=today)
    ).annotate(
        priority=Case(
            When(status='new', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('priority', '-created_at')

    stats = {
        'new': Order.objects.filter(status='new').count(),
        'packed': Order.objects.filter(status='packed').count(),
        'given': Order.objects.filter(status='given').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }

    show_all = request.GET.get('all', '0') == '1'
    if show_all:
        orders = Order.objects.all().order_by('-created_at')

    context = {
        'orders': orders,
        'stats': stats,
        'show_all': show_all,
        'today_orders_count': orders.filter(created_at__date=today).count(),
        'new_orders_count': orders.filter(status='new').count(),
    }
    return render(request, 'store/seller/dashboard.html', context)


@staff_member_required
def seller_order_detail(request, uuid):
    """
    Детали заказа для продавца
    """
    order = get_object_or_404(Order, uuid=uuid)
    packages = order.packages.all()

    qr_order = qrcode.make(order.get_qr_data())
    buffer = BytesIO()
    qr_order.save(buffer, format='PNG')
    order_qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(
        request,
        'store/seller/order_detail.html',
        {
            'order': order,
            'packages': packages,
            'order_qr_base64': order_qr_base64,
        }
    )


@staff_member_required
def seller_assemble(request, order_uuid):
    """
    Страница сборки заказа для продавца
    """
    order = get_object_or_404(Order, uuid=order_uuid)

    if order.status == 'packed':
        return redirect('store:seller_order_detail', uuid=order.uuid)

    expected_items = order.items.select_related('product').all()
    assembled_items = []

    context = {
        'order': order,
        'expected_items': expected_items,
        'assembled_items': assembled_items,
    }
    return render(request, 'store/seller/assemble.html', context)


@staff_member_required
def seller_verify_qr(request):
    """
    Страница проверки QR при выдаче
    """
    return render(request, 'store/seller/verify.html')