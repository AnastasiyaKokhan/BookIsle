import datetime

from django import forms
from django.contrib.auth.models import User

from .models import Profile
from .validators import validate_passport_number


# from django.core.exceptions import ValidationError


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True, label='Имя*')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия*')
    patronymic = forms.CharField(max_length=30, required=False,  label='Отчество')
    residential_address = forms.CharField(label='Адрес проживания', required=False,
                                          widget=forms.TextInput(attrs={'placeholder': 'город, улица дом - квартира'}))
    passport_number = forms.CharField(max_length=9, required=False, label='Номер паспорта',
                                      validators=[validate_passport_number],
                                      widget=forms.TextInput(attrs={'placeholder': 'АА0000000'}))
    birth_date = forms.DateField(required=True, label='День рождения*',
                                 widget=forms.SelectDateWidget(years=range(datetime.date.today().year-100, datetime.date.today().year-18)))
    email = forms.EmailField(required=True, label='Email*')
    is_agreed = forms.BooleanField(required=True, label='Пользователь подписал соглашение')

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get("passport_number")
        if passport_number:
            if Profile.objects.filter(passport_number=passport_number).exists():
                raise forms.ValidationError("Пользователь с таким паспортным номером уже существует")
            return passport_number

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(groups__name='reader', email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email


class SignInForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
