from django.shortcuts import render


def about(request):
    """
        О магазине
    """

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'cart_count': cart_count,
    }

    return render(request, 'store/about.html', context)