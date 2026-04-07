from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from store.models import Order, Client


def order_detail(request, uuid):
    """
    Детали заказа
    """
    order = get_object_or_404(Order, uuid=uuid)

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'order': order,
        'cart_count': cart_count,
    }
    return render(request, 'store/user/order_detail.html', context)


@login_required
def my_orders(request):
    client = getattr(request.user, 'client_profile', None)

    if not client and request.user.email:
        client = Client.objects.filter(email=request.user.email).first()
        if client and not client.user:
            client.user = request.user
            client.save()

    if client:
        orders = Order.objects.filter(client=client).order_by('-created_at')
    else:
        orders = Order.objects.none()

    active_orders = orders.filter(status__in=['new', 'packed']).count()

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/user/my_orders.html', {
        'page_obj': page_obj,
        'orders_count': orders.count(),
        'active_orders': active_orders,
    })