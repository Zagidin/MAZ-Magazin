# store/views/api/sync_1c.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from store.models import Product, Order, Client
from django.utils import timezone


# Это пример API endpoint'а, который будет вызывать 1С
@csrf_exempt
@require_POST
def sync_orders_from_1c(request):
    """
    API для получения заказов из 1С.
    1С отправляет POST запрос с JSON списком заказов.
    """
    try:
        data = json.loads(request.body)
        # Здесь должна быть логика парсинга данных из 1С
        # Пример: создание заказа, если его нет в базе

        # mock-ответ для демонстрации
        return JsonResponse({
            'status': 'success',
            'message': f'Получено {len(data.get("orders", []))} заказов из 1С',
            'processed': True
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_GET
def sync_products_to_1c(request):
    """
    API для отправки актуальных остатков в 1С.
    1С запрашивает этот URL, чтобы обновить свои базы.
    """
    try:
        # Выгружаем все активные товары с остатками
        products = Product.objects.filter(is_active=True).values('id', 'article', 'name', 'quantity', 'guid_1c')

        return JsonResponse({
            'status': 'success',
            'count': len(products),
            'data': list(products)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def update_status_in_1c(request, order_id):
    """
    Уведомление 1С об изменении статуса заказа (например, 'Выдан').
    """
    try:
        order = Order.objects.get(id=order_id)
        # Логика отправки статуса в 1С...

        return JsonResponse({
            'status': 'success',
            'message': f'Статус заказа {order.uuid} обновлен в 1С на {order.status}'
        })
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден'}, status=404)