import qrcode
import base64
from io import BytesIO
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category,
    EquipmentType,
    Product,
    Client,
    Order,
    OrderItem,
    OrderPackage,
    SyncLog
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'guid_1c']
    search_fields = ['name']


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'guid_1c']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'name', 'price', 'quantity', 'is_active', 'category']
    list_filter = ['is_active', 'category', 'equipment_type']
    search_fields = ['article', 'name', 'guid_1c']
    list_editable = ['quantity', 'price']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'phone', 'created_at']
    search_fields = ['phone', 'last_name', 'email']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['uuid_short', 'client', 'total', 'status', 'created_at', 'is_synced_1c']
    list_filter = ['status', 'is_synced_1c', 'created_at']
    search_fields = ['uuid', 'client__phone', 'client__last_name']
    readonly_fields = ['uuid', 'qr_code_display', 'created_at']
    inlines = [OrderItemInline]
    actions = ['generate_package']

    def uuid_short(self, obj):
        return f"№{obj.uuid.hex[:8]}"
    uuid_short.short_description = "Номер"

    def qr_code_display(self, obj):
        qr = qrcode.make(obj.get_qr_data())
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        return format_html(f'<img src="data:image/png;base64,{img_str}" width="150" />')
    qr_code_display.short_description = "QR-код заказа"

    def generate_package(self, request, queryset):
        for order in queryset:
            if order.status == 'new':
                OrderPackage.objects.get_or_create(
                    order=order,
                    defaults={'package_number': '1/1'}
                )
                order.status = 'packed'
                order.save()
        self.message_user(request, "✅ Упаковки созданы, статус изменён на 'Собран'")
    generate_package.short_description = "Сформировать упаковку"


@admin.register(OrderPackage)
class OrderPackageAdmin(admin.ModelAdmin):
    list_display = ['package_number', 'order', 'is_printed', 'created_at']
    list_filter = ['is_printed']
    readonly_fields = ['uuid', 'qr_code_display']

    def qr_code_display(self, obj):
        qr = qrcode.make(obj.get_qr_data())
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        return format_html(f'<img src="data:image/png;base64,{img_str}" width="150" />')
    qr_code_display.short_description = "QR-код пакета"


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'success', 'created_at']
    list_filter = ['action', 'success']
    readonly_fields = ['created_at']