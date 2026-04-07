from django.db.models import Q
from store.models import Product
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required



@staff_member_required
def product_by_article_api(request):
    """
    API: Поиск товара по артикулу или названию
    """
    article = request.GET.get('article', '').strip()

    if not article:
        return JsonResponse({'error': 'Введите артикул'}, status=400)

    try:
        product = Product.objects.get(
            Q(article__iexact=article) | Q(article=article),
            is_active=True
        )

        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'article': product.article,
                'name': product.name,
                'category': product.category.name,
                'equipment_type': product.equipment_type.name,
                'price': str(product.price),
                'quantity': product.quantity,
                'image': product.image.url if product.image else None,
                'guid_1c': product.guid_1c,
            }
        })

    except Product.DoesNotExist:
        products = Product.objects.filter(
            Q(name__icontains=article) | Q(article__icontains=article),
            is_active=True
        )[:5]

        if products:
            return JsonResponse({
                'success': False,
                'error': 'Товар не найден точно. Возможно, вы имели в виду:',
                'suggestions': [
                    {
                        'article': p.article,
                        'name': p.name,
                        'equipment_type': p.equipment_type.name,
                    }
                    for p in products
                ]
            })

        return JsonResponse({
            'success': False,
            'error': 'Товар не найден'
        }, status=404)