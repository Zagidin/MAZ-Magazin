import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from store.models import Product


@require_POST
@csrf_exempt
def cart_add_api(request, product_id):
    """
    API: Добавить товар в корзину
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)

        if product.quantity <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Товар закончился'
            })

        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
            'message': f'{product.name} добавлен в корзину'
        })

    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Товар не найден'
        })


@require_GET
def cart_count_api(request):
    """
    API: Количество товаров в корзине
    """
    cart = request.session.get('cart', {})
    return JsonResponse({'count': sum(cart.values())})


@require_GET
def cart_items_api(request):
    """
    API: Список товаров в корзине
    """
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = float(product.price) * qty
            total += item_total

            items.append({
                'product_id': product.id,
                'product_name': product.name,
                'price': str(product.price),
                'quantity': qty,
                'item_total': str(item_total),
            })
        except Product.DoesNotExist:
            pass

    return JsonResponse({
        'items': items,
        'total': str(total),
        'count': sum(cart.values()),
    })


@require_POST
@csrf_exempt
def cart_remove_api(request, product_id):
    """
    API: Удалить товар из корзины
    """
    try:
        cart = request.session.get('cart', {})
        cart.pop(str(product_id), None)
        request.session['cart'] = cart
        request.session.modified = True

        total = 0
        count = 0

        for pid, qty in cart.items():
            try:
                p = Product.objects.get(id=pid, is_active=True)
                total += p.price * qty
                count += qty
            except Product.DoesNotExist:
                pass

        return JsonResponse({
            'success': True,
            'cart_total': total,
            'cart_count': count,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
@csrf_exempt
def cart_update_api(request, product_id):
    """
    API: Обновить количество товара в корзине
    Ожидает JSON: {"quantity": 2}
    """
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        cart = request.session.get('cart', {})

        if str(product_id) not in cart:
            return JsonResponse({
                'success': False,
                'error': 'Товар не найден'
            }, status=404)

        if quantity <= 0:
            del cart[str(product_id)]
        else:
            product = Product.objects.get(id=product_id, is_active=True)
            if quantity > product.quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Максимум {product.quantity} шт. в наличии'
                }, status=400)
            cart[str(product_id)] = quantity

        request.session['cart'] = cart
        request.session.modified = True

        total = 0
        count = 0
        item_total = 0

        for pid, qty in cart.items():
            p = Product.objects.get(id=pid, is_active=True)
            if pid == str(product_id):
                item_total = p.price * qty
            total += p.price * qty
            count += qty

        return JsonResponse({
            'success': True,
            'item_total': item_total,
            'cart_total': total,
            'cart_count': count,
        })

    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Товар не найден'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)