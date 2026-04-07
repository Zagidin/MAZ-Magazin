from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from store.forms import LoginForm, RegisterForm
from store.models import Client


def login_view(request):
    """
    Вход пользователя
    """
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'✅ С возвращением, {user.username}!')

            next_url = request.GET.get('next', 'store:index')
            return redirect(next_url)
    else:
        form = LoginForm()

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    context = {
        'form': form,
        'cart_count': cart_count,
    }
    return render(request, 'store/auth/login.html', context)


def logout_view(request):
    """
    Выход пользователя
    """
    logout(request)
    messages.info(request, '👋 Вы вышли из системы')
    return redirect('store:index')


def register(request):
    """
    Регистрация пользователя
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            phone = form.cleaned_data.get('phone', '')
            if phone:
                Client.objects.get_or_create(
                    phone=phone,
                    defaults={
                        'first_name': form.cleaned_data.get('first_name', ''),
                        'last_name': form.cleaned_data.get('last_name', ''),
                        'patronymic': form.cleaned_data.get('patronymic', ''),
                        'email': user.email,
                    }
                )

            login(request, user)
            messages.success(request, '✅ Регистрация успешна!')
            return redirect('store:index')
    else:
        form = RegisterForm()

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    return render(
        request,
        'store/auth/register.html',
        {
            'form': form,
            'cart_count': cart_count,
        }
    )