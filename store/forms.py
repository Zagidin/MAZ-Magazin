from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm
)
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """
        Форма регистрации пользователя
    """

    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Придумайте логин'
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Придумайте пароль'
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Повторите пароль'
            }
        )
        self.fields['phone'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': '+7 (___) ___-__-__'
            }
        )


class LoginForm(AuthenticationForm):
    """
        Форма входа
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите логин'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })


class CheckoutForm(forms.Form):
    """
        Форма оформления заказа
    """

    first_name = forms.CharField(max_length=100, required=True, label='Имя')
    last_name = forms.CharField(max_length=100, required=True, label='Фамилия')
    patronymic = forms.CharField(max_length=100, required=False, label='Отчество')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    email = forms.EmailField(required=False, label='Email')
    delivery = forms.ChoiceField(
        choices=[
            ('pickup', 'Самовывоз'),
            ('delivery', 'Доставка')
        ],
        required=True,
        label='Способ получения'
    )
    address = forms.CharField(widget=forms.Textarea, required=False, label='Адрес доставки')
    payment = forms.ChoiceField(
        choices=[
            ('cash', 'Наличные'),
            ('card', 'Карта')
        ],
        required=True,
        label='Способ оплаты'
    )
    comment = forms.CharField(widget=forms.Textarea, required=False, label='Комментарий')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'comment':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})