from django.contrib import messages
from django.shortcuts import render, redirect

from store.forms import CheckoutForm
from store.models import (
    Product,
    Client,
    Order,
    OrderPackage,
    OrderItem,
)


def cart_page(request):
    """
    Страница корзины
    """
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * qty
            total += item_total
            items.append({
                'product': product,
                'quantity': qty,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass

    cart_count = sum(cart.values())

    context = {
        'items': items,
        'total': total,
        'cart_count': cart_count,
    }
    return render(request, 'store/user/cart.html', context)


def checkout(request):
    """
    Оформление заказа
    """
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, '❌ Корзина пуста!')
        return redirect('store:cart')

    items = []
    total = 0
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * qty
            total += item_total
            items.append({
                'product': product,
                'quantity': qty,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            phone = form.cleaned_data['phone']

            client, created = Client.objects.get_or_create(
                phone=phone,
                defaults={
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'patronymic': form.cleaned_data.get('patronymic', ''),
                    'email': form.cleaned_data.get('email', ''),
                }
            )

            if not created:
                client.first_name = form.cleaned_data['first_name']
                client.last_name = form.cleaned_data['last_name']
                client.patronymic = form.cleaned_data.get('patronymic', '')
                client.email = form.cleaned_data.get('email', '')
                client.save()

            if request.user.is_authenticated and not client.user:
                client.user = request.user
                client.save()

            order = Order.objects.create(
                client=client,
                status='new',
                total=total,
            )

            for product_id, qty in cart.items():
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=product.price,
                    )
                except Product.DoesNotExist:
                    pass

            OrderPackage.objects.create(
                order=order,
                package_number='1/1',
            )

            request.session['cart'] = {}
            request.session.modified = True
            request.session['last_order_uuid'] = str(order.uuid)

            messages.success(request, f'✅ Заказ оформлен! Номер: {order.uuid.hex[:8]}')
            return redirect('store:order_detail', uuid=order.uuid)
    else:
        form = CheckoutForm()

    cart_count = sum(cart.values())

    context = {
        'form': form,
        'items': items,
        'total': total,
        'cart_count': cart_count,
        'user': request.user,
    }
    return render(request, 'store/user/checkout.html', context)