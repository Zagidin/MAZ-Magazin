from django.shortcuts import render


def contacts(request):
    """
        Контакты
    """

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'cart_count': cart_count,
    }

    return render(request, 'store/contacts.html', context)