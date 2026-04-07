from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET

from store.models import Order


@require_GET
def order_updates_api(request, order_uuid):
    """
    API: Проверить изменения заказа
    """
    order = get_object_or_404(Order, uuid=order_uuid)

    return JsonResponse({
        'status': order.status,
        'status_display': order.get_status_display(),
        'total': str(order.total),
        'items_count': order.items.count(),
        'updated_at': (
            order.updated_at.isoformat()
            if hasattr(order, 'updated_at')
            else order.created_at.isoformat()
        ),
    })


@staff_member_required
@require_GET
def orders_updates_api(request):
    """
    API: Проверить новые заказы для дашборда
    """
    orders = Order.objects.all().order_by('-created_at')

    new_orders_count = orders.filter(
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).count()

    new_for_assembly = orders.filter(status='new').count()

    return JsonResponse({
        'total_orders': orders.count(),
        'new_orders_count': new_orders_count,
        'new_for_assembly': new_for_assembly,
        'has_updates': new_orders_count > 0,
        'timestamp': timezone.now().isoformat(),
    })