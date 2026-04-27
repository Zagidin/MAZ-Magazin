import uuid
import json
import qrcode
from io import BytesIO
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from store.models import Order, OrderItem, OrderPackage, Product
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
@require_POST
def seller_finish_assembly(request, order_uuid):
    """
        Завершить сборку: атомарно списать товары по позициям заказа
    """

    order = get_object_or_404(Order, uuid=order_uuid)

    if order.status != 'new':
        messages.error(request, 'Заказ уже обработан или отменён.')
        return redirect('store:seller_dashboard')

    with transaction.atomic():
        # Блокируем все товары, фигурирующие в заказе
        items = order.items.select_related('product').all()
        product_ids = [item.product_id for item in items]
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        for item in items:
            product = product_map[item.product_id]
            if product.quantity < item.quantity:
                messages.error(request, f'❌ Недостаточно товара «{product.name}» на складе.')
                return redirect('store:seller_assemble', order_uuid=order_uuid)
            product.quantity -= item.quantity
            product.save(update_fields=['quantity'])

        order.status = 'packed'
        order.save(update_fields=['status'])

        OrderPackage.objects.get_or_create(
            order=order,
            defaults={'package_number': '1/1'}
        )

    messages.success(request, '✅ Заказ собран, товары списаны.')
    return redirect('store:seller_order_detail', uuid=order.uuid)


@staff_member_required
def seller_pack_order(request, uuid):
    """
        Собрать заказ (сменить статус на packed)
    """
    order = get_object_or_404(Order, uuid=uuid)

    if order.status == 'new':
        order.status = 'packed'
        order.save()

        OrderPackage.objects.get_or_create(
            order=order,
            defaults={'package_number': '1/1'}
        )

        messages.success(request, '✅ Заказ собран! Пакет создан.')
    else:
        messages.info(request, f'Заказ уже в статусе: {order.get_status_display()}')

    return redirect('store:seller_order_detail', uuid=order.uuid)


@staff_member_required
def seller_print_qr(request, uuid):
    """
        Печать QR-кода для пакета
    """
    package = get_object_or_404(OrderPackage, uuid=uuid)

    qr = qrcode.make(package.get_qr_data())
    buffer = BytesIO()
    qr.save(buffer, format='PNG')

    return HttpResponse(buffer.getvalue(), content_type='image/png')

@staff_member_required
@require_POST
def order_add_item_api(request, order_uuid):
    """
        API: Добавить товар при сборке (проверка, без списания)
    """

    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, uuid=order_uuid)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        product = Product.objects.get(id=product_id, is_active=True)

        # 1. Проверить, есть ли товар в исходном заказе
        try:
            order_item = OrderItem.objects.get(order=order, product_id=product_id)
            ordered_qty = order_item.quantity
        except OrderItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'❌ Товар {product.article} не входит в этот заказ!'
            }, status=400)

        # 2. Проверить, не превышает ли добавляемое количество заказанное
        #    (можно запоминать, сколько уже отсканировано, но проще доверять сборщику)
        #    Однако базовая проверка лишней не будет
        if quantity > order_item.quantity:
            return JsonResponse({
                'success': False,
                'error': f'❌ Нельзя добавить больше, чем в заказе ({order_item.quantity} шт.)'
            }, status=400)

        # 3. Проверить остаток на складе (без списания!)
        if product.quantity < quantity:
            return JsonResponse({
                'success': False,
                'error': f'❌ Недостаточно на складе! Осталось: {product.quantity} шт.'
            }, status=400)

        # НЕ СПИСЫВАЕМ – просто возвращаем успех
        return JsonResponse({
            'success': True,
            'message': f'✅ {product.name} проверен ({quantity} шт.)',
            'item': {
                'name': product.name,
                'article': product.article,
                'quantity': quantity,
                'price': str(product.price),
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def scan_verify(request):
    """
        API для проверки QR-кодов при выдаче
    """
    try:
        data = json.loads(request.body)
        order_qr = data.get('order_qr')
        package_qr = data.get('package_qr')

        if not order_qr or not package_qr:
            return JsonResponse({
                'status': 'error',
                'message': 'Не переданы QR-коды'
            })

        order = Order.objects.get(uuid=uuid.UUID(order_qr))
        package = OrderPackage.objects.get(uuid=uuid.UUID(package_qr))

        if package.order != order:
            return JsonResponse({
                'status': 'error',
                'message': '❌ ОШИБКА: Пакет не соответствует заказу!',
                'order': str(order),
                'package_order': str(package.order),
            })

        if order.status != 'packed':
            return JsonResponse({
                'status': 'error',
                'message': f'⚠️ Статус заказа: {order.status}. Нельзя выдать.'
            })

        order.status = 'given'
        order.given_at = timezone.now()
        order.save()

        return JsonResponse({
            'status': 'success',
            'message': '✅ ВСЁ ВЕРНО! Можно выдавать товар.',
            'order': str(order),
            'client': str(order.client),
            'total': str(order.total),
        })

    except Order.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '❌ Заказ не найден'
        })

    except OrderPackage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '❌ Пакет не найден'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'❌ Ошибка: {str(e)}'
        })