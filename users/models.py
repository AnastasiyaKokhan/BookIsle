from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    patronymic = models.CharField(max_length=30, blank=True, null=True, verbose_name='Отчество')
    passport_number = models.CharField(max_length=9, unique=True, blank=True, null=True, verbose_name='Номер паспорта',
                                       help_text='АА0000000')
    birth_date = models.DateField(verbose_name='Дата рождения', help_text='ДД.ММ.ГГГГ')
    residential_address = models.CharField(max_length=500, blank=True, null=True, verbose_name='Адрес проживания',
                                           help_text='населенный пункт, улица, дом, квартира')
    is_agreed = models.BooleanField(default=False, verbose_name='Пользователь подписал соглашение')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Профиль читателя'
        verbose_name_plural = 'Профиль читателей'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
