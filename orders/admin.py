from django.contrib import admin

from .models import OrderItem, Order, BookReturn, DamagePhoto


# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['book_instance']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'reader', 'issue_date', 'return_date']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)


class DamagePhotoInline(admin.TabularInline):
    model = DamagePhoto
    raw_id_fields = ['book_damage']


class BookReturnAdmin(admin.ModelAdmin):
    list_display = ['id', 'book_instance', 'return_date', 'reader_assessment', 'damage_description']
    inlines = [DamagePhotoInline]


admin.site.register(BookReturn, BookReturnAdmin)

