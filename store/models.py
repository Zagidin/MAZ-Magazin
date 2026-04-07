import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    guid_1c = models.CharField(max_length=36, blank=True, default='', verbose_name="GUID в 1С", db_index=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    guid_1c = models.CharField(max_length=36, blank=True, default='', verbose_name="GUID в 1С")

    class Meta:
        verbose_name = "Тип техники"
        verbose_name_plural = "Типы техники"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    article = models.CharField(max_length=50, unique=True, verbose_name="Артикул", db_index=True)
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name="Категория")
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.PROTECT, related_name='products', verbose_name="Тип техники")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Остаток")
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True, verbose_name="Фото")
    guid_1c = models.CharField(max_length=36, blank=True, default='', verbose_name="GUID в 1С", db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']
        indexes = [
            models.Index(fields=['article']),
            models.Index(fields=['is_active', 'quantity']),
        ]

    def __str__(self):
        return f"{self.article} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.guid_1c:
            self.guid_1c = str(uuid.uuid4())
        super().save(*args, **kwargs)


class Client(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон", db_index=True)  # ← unique остаётся!
    email = models.EmailField(blank=True, verbose_name="E-mail")
    guid_1c = models.CharField(max_length=36, blank=True, default='', verbose_name="GUID в 1С")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    # СВЯЗЬ С ПОЛЬЗОВАТЕЛЕМ
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_profile',
        verbose_name="Пользователь"
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def save(self, *args, **kwargs):
        if not self.guid_1c:
            self.guid_1c = str(uuid.uuid4())
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', '🆕 Новый'),
        ('packed', '📦 Собран'),
        ('given', '✅ Выдан'),
        ('cancelled', '❌ Отменен'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID заказа")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='orders', verbose_name="Клиент")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Итого")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    given_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата выдачи")
    guid_1c = models.CharField(max_length=36, blank=True, default='', verbose_name="GUID в 1С")
    is_synced_1c = models.BooleanField(default=False, verbose_name="Отправлен в 1С")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.uuid.hex[:8]} от {self.created_at.strftime('%d.%m.%Y')}"

    def get_qr_data(self):
        return str(self.uuid)

    def calculate_total(self):
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total = total
        self.save(update_fields=['total'])
        return total

    def save(self, *args, **kwargs):
        if not self.guid_1c:
            self.guid_1c = str(uuid.uuid4())
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items', verbose_name="Товар")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Количество")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена на момент покупки")
    guid_1c = models.CharField(max_length=36, blank=True, default='', verbose_name="GUID в 1С")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.guid_1c:
            self.guid_1c = str(uuid.uuid4())
        super().save(*args, **kwargs)


class OrderPackage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='packages', verbose_name="Заказ")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID пакета")
    package_number = models.CharField(max_length=10, default='1/1', verbose_name="Номер пакета")
    is_printed = models.BooleanField(default=False, verbose_name="QR напечатан")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Упаковка заказа"
        verbose_name_plural = "Упаковки заказов"

    def __str__(self):
        return f"Пакет {self.package_number} для заказа {self.order.uuid.hex[:8]}"

    def get_qr_data(self):
        return str(self.uuid)


class SyncLog(models.Model):
    ACTION_CHOICES = [
        ('order_create', 'Создание заказа'),
        ('order_status', 'Обновление статуса'),
        ('product_sync', 'Обновление товаров'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Действие")
    data = models.TextField(verbose_name="JSON данные")
    success = models.BooleanField(default=False, verbose_name="Успешно")
    error_message = models.TextField(blank=True, verbose_name="Ошибка")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лог синхронизации"
        verbose_name_plural = "Логи синхронизации"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {'✅' if self.success else '❌'}"