import uuid
import json
import qrcode
import logging
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
    Завершить сборку + списать товары
    """
    order = get_object_or_404(Order, uuid=order_uuid)

    with transaction.atomic():
        for item in order.items.all():
            product = item.product
            if product.quantity >= item.quantity:
                product.quantity -= item.quantity
                product.save()
            else:
                messages.error(request, f'❌ Недостаточно: {product.name}')
                return redirect('store:seller_assemble', order_uuid=order_uuid)

        order.status = 'packed'
        order.save()

        OrderPackage.objects.get_or_create(
            order=order,
            defaults={'package_number': '1/1'}
        )

    messages.success(request, '✅ Заказ собран!')
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


# @staff_member_required
# @require_POST
# def order_add_item_api(request, order_uuid):
#     """
#     API: Добавить/подтвердить товар при сборке
#     """
#     logger = logging.getLogger(__name__)
#
#     try:
#         data = json.loads(request.body)
#         order = get_object_or_404(Order, uuid=order_uuid)
#         product_id = data.get('product_id')
#         quantity = int(data.get('quantity', 1))
#
#         product = Product.objects.get(id=product_id, is_active=True)
#
#         if product.quantity < quantity:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'Недостаточно на складе! Осталось: {product.quantity} шт.'
#             }, status=400)
#
#         order_item, created = OrderItem.objects.get_or_create(
#             order=order,
#             product=product,
#             defaults={'quantity': quantity, 'price': product.price}
#         )
#
#         product.quantity -= quantity
#         product.save()
#
#         if not created:
#             logger.info(f"✅ Подтверждено: {order_item.product.name}")
#             message = f'✅ {product.name} подтверждён ({quantity} шт. списано)'
#         else:
#             logger.info(f"✅ Добавлено: {product.name}")
#             message = f'✅ {product.name} добавлен ({quantity} шт.)'
#
#         order.calculate_total()
#
#         return JsonResponse({
#             'success': True,
#             'already_in_package': False,
#             'message': message,
#             'item': {
#                 'name': product.name,
#                 'article': product.article,
#                 'quantity': order_item.quantity,
#                 'price': str(product.price),
#             }
#         })
#
#     except Exception as e:
#         logger.error(f"❌ Ошибка: {str(e)}")
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=500)
# @staff_member_required
# @require_POST
# def order_add_item_api(request, order_uuid):
#     """API: Добавить товар при сборке — НЕ БОЛЬШЕ, чем заказал клиент"""
#     from django.shortcuts import get_object_or_404
#     import logging
#     logger = logging.getLogger(__name__)
#
#     try:
#         data = json.loads(request.body)
#         order = get_object_or_404(Order, uuid=order_uuid)
#         product_id = data.get('product_id')
#         quantity = int(data.get('quantity', 1))
#
#         logger.info(f"📦 Сборка: product_id={product_id}, quantity={quantity}")
#
#         product = Product.objects.get(id=product_id, is_active=True)
#
#         # 🔥 ПРОВЕРКА #1: Есть ли этот товар в заказе клиента?
#         try:
#             order_item = OrderItem.objects.get(order=order, product_id=product_id)
#             ordered_qty = order_item.quantity  # 🔥 Сколько заказал клиент
#         except OrderItem.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'❌ Товар {product.article} не входит в этот заказ!'
#             }, status=400)
#
#         # 🔥 ПРОВЕРКА #2: Не пытаемся ли добавить больше, чем заказано?
#         # (Для точного учёта нужно поле assembled_qty, но пока блокируем повторное добавление)
#         already_in_order = OrderItem.objects.filter(
#             order=order,
#             product_id=product_id
#         ).exists()
#
#         if already_in_order and quantity > 0:
#             # Если товар уже есть в заказе — не даём добавить ещё
#             return JsonResponse({
#                 'success': False,
#                 'error': f'⚠️ {product.name} уже в заказе (заказано: {ordered_qty} шт.)'
#             }, status=400)
#
#         # 🔥 ПРОВЕРКА #3: Хватит ли на складе?
#         if product.quantity < quantity:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'❌ Недостаточно на складе! Осталось: {product.quantity} шт.'
#             }, status=400)
#
#         # 🔥 СПИСЫВАЕМ СО СКЛАДА (только один раз!)
#         product.quantity -= quantity
#         product.save()
#
#         logger.info(f"✅ Списано: {product.name} — {quantity} шт.")
#
#         return JsonResponse({
#             'success': True,
#             'message': f'✅ {product.name} добавлен ({quantity} шт.)',
#             'item': {
#                 'name': product.name,
#                 'article': product.article,
#                 'quantity': quantity,
#                 'price': str(product.price),
#                 'ordered': ordered_qty,  # Для отображения в интерфейсе
#             }
#         })
#
#     except Exception as e:
#         logger.error(f"❌ Ошибка: {str(e)}")
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)
@staff_member_required
@require_POST
def order_add_item_api(request, order_uuid):
    """API: Добавить товар при сборке — ТОЛЬКО по кнопке, НЕ БОЛЬШЕ заказа"""
    from django.shortcuts import get_object_or_404
    import logging
    logger = logging.getLogger(__name__)

    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, uuid=order_uuid)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))

        product = Product.objects.get(id=product_id, is_active=True)

        # 🔥 ПРОВЕРКА #1: Есть ли этот товар в заказе клиента?
        try:
            order_item = OrderItem.objects.get(order=order, product_id=product_id)
            ordered_qty = order_item.quantity  # Сколько заказал клиент
        except OrderItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'❌ Товар {product.article} не входит в этот заказ!'
            }, status=400)

        # 🔥 ПРОВЕРКА #2: Хватит ли на складе?
        if product.quantity < quantity:
            return JsonResponse({
                'success': False,
                'error': f'❌ Недостаточно на складе! Осталось: {product.quantity} шт.'
            }, status=400)

        # 🔥 СПИСЫВАЕМ СО СКЛАДА
        product.quantity -= quantity
        product.save()

        logger.info(f"✅ Списано: {product.name} — {quantity} шт.")

        return JsonResponse({
            'success': True,
            'message': f'✅ {product.name} добавлен ({quantity} шт.)',
            'item': {
                'name': product.name,
                'article': product.article,
                'quantity': quantity,
                'price': str(product.price),
            }
        })

    except Exception as e:
        logger.error(f"❌ Ошибка: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# @staff_member_required
# @require_POST
# def order_add_item_api(request, order_uuid):
#     """API: Добавить товар при сборке — ТОЛЬКО по кнопке"""
#     from django.shortcuts import get_object_or_404
#     import logging
#     logger = logging.getLogger(__name__)
#
#     try:
#         data = json.loads(request.body)
#         order = get_object_or_404(Order, uuid=order_uuid)
#         product_id = data.get('product_id')
#         quantity = int(data.get('quantity', 1))
#
#         product = Product.objects.get(id=product_id, is_active=True)
#
#         # ПРОВЕРКА #1: Есть ли этот товар в заказе клиента?
#         try:
#             order_item = OrderItem.objects.get(order=order, product_id=product_id)
#             ordered_qty = order_item.quantity
#         except OrderItem.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'❌ Товар {product.article} не входит в этот заказ!'
#             }, status=400)
#
#         # ПРОВЕРКА #2: Хватит ли на складе?
#         if product.quantity < quantity:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'❌ Недостаточно на складе! Осталось: {product.quantity} шт.'
#             }, status=400)
#
#         # СПИСЫВАЕМ СО СКЛАДА
#         product.quantity -= quantity
#         product.save()
#
#         logger.info(f"✅ Списано: {product.name} — {quantity} шт.")
#
#         return JsonResponse({
#             'success': True,
#             'message': f'✅ {product.name} добавлен ({quantity} шт.)',
#             'item': {
#                 'name': product.name,
#                 'article': product.article,
#                 'quantity': quantity,
#                 'price': str(product.price),
#                 'image': product.image.url if product.image else None,
#             }
#         })
#
#     except Exception as e:
#         logger.error(f"❌ Ошибка: {str(e)}")
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


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