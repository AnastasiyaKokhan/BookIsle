import datetime

from django.db import models


from django.contrib.auth.models import User
from django.utils import timezone

from main.models import BookInstance


# Create your models here.


class CartItem(models.Model):
    book_instance = models.OneToOneField(BookInstance, on_delete=models.CASCADE, verbose_name='Экземпляр книги')

    def __str__(self):
        return f'Экземпляр книги: {self.book_instance.id}'

    def count_price_per_month(self):
        return self.book_instance.price_per_day * 30

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book_instance.status = "in_cart"
        self.book_instance.save()

    def delete(self, *args, **kwargs):
        self.book_instance.status = "available"
        self.book_instance.save()
        super().delete(*args, **kwargs)


class OrderItem(models.Model):
    book_instance = models.OneToOneField(BookInstance, on_delete=models.CASCADE, verbose_name='Экземпляр книги')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name='Заказ')

    def __str__(self):
        return f'Экземпляр книги №{self.book_instance.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book_instance.status = "not_available"
        self.book_instance.save()


class Order(models.Model):
    reader = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Читатель')
    issue_date = models.DateField(auto_now_add=True, verbose_name='Дата выдачи')
    return_date = models.DateField(verbose_name='Дата возврата')

    class Meta:
        ordering = ('-issue_date',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Номер заказа: {self.id}'

    def save(self, *args, **kwargs):
        if not self.return_date:
            self.return_date = datetime.date.today() + datetime.timedelta(days=30)
        super().save(*args, **kwargs)


class BookReturn(models.Model):
    STARS = {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
    }
    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, verbose_name='Экземпляр книги')
    return_date = models.DateField(default=timezone.now, verbose_name='Дата возврата')
    reader_assessment = models.CharField(max_length=1, choices=STARS, blank=True, null=True, verbose_name='Оценка')
    damage_description = models.TextField(blank=True, null=True, verbose_name='Описание повреждений')
    book_instance_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00,
                                              verbose_name='Цена за использование книгу')

    class Meta:
        verbose_name = 'Возврат'
        verbose_name_plural = 'Возвраты'

    def __str__(self):
        return f'Экземпляр книги: {self.book_instance.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book_instance.status = "available"
        self.book_instance.save()


class DamagePhoto(models.Model):
    book_damage = models.ForeignKey('BookReturn', on_delete=models.CASCADE, verbose_name='Поврежедния')
    photo = models.ImageField(upload_to='book_damages/', verbose_name='Фотография')

    class Meta:
        verbose_name = 'Фотография повреждения'
        verbose_name_plural = 'Фотографии повреждений'

    def __str__(self):
        return f'Экземпляр книги: {self.book_damage.book_instance.id}'
