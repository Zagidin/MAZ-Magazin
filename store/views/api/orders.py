from django.http import JsonResponse
from store.models import Order, Product
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET


@require_GET
def order_api(request, uuid):
    """
    API: Данные заказа для модалки
    """
    order = get_object_or_404(Order, uuid=uuid)

    return JsonResponse({
        'uuid': str(order.uuid),
        'number': order.uuid.hex[:8],
        'total': str(order.total),
        'status': order.get_status_display(),
        'client': str(order.client),
        'items_count': order.items.count(),
    })


@require_GET
def product_api(request, pk):
    """
    API: Данные товара для модального окна
    """
    try:
        product = Product.objects.get(pk=pk, is_active=True)

        html = f"""
            <div class="product-modal-detail">
                <div class="modal-product-image">
                    {'<img src="' + product.image.url + '" alt="' + product.name + '">' if product.image else '<img src="/static/img/no-image.png" alt="' + product.name + '">'}
                </div>
                <div class="modal-product-info">
                    <h2>{product.name}</h2>
                    <p class="article">Артикул: {product.article}</p>
                    <p class="price">{product.price} ₽</p>
                    <p class="description">{product.description or 'Описание отсутствует'}</p>
                    <p class="stock">В наличии: {product.quantity} шт.</p>
                    <button class="btn btn-primary btn-lg" onclick="addToCart({product.id}); closeProductModal();">
                        <i class="fas fa-cart-plus"></i> Добавить в корзину
                    </button>
                </div>
            </div>
        """

        return JsonResponse({
            'html': html,
            'success': True,
        })

    except Product.DoesNotExist:
        return JsonResponse({
            'html': '<p>Товар не найден</p>',
            'success': False,
        })