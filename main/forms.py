from django import forms
from django.forms import CheckboxSelectMultiple
from mptt.forms import TreeNodeMultipleChoiceField
from django.utils import timezone

from .models import Genre, Author


class AddBookForm(forms.Form):
    russian_title = forms.CharField(max_length=300, required=True, label='На русском языке')
    original_title = forms.CharField(max_length=300, required=False, label='На языке оригинала')
    book_photos = forms.ImageField(required=True)
    search_authors = forms.CharField(max_length=100, required=False, help_text='Поиск авторов')
    authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False, widget=CheckboxSelectMultiple)
    new_author_last_name = forms.CharField(max_length=30, required=False, help_text='Фамилия')
    new_author_first_name = forms.CharField(max_length=30, required=False, help_text='Имя')
    new_author_patronymic = forms.CharField(max_length=30, required=False, help_text='Отчество')
    new_author_photos = forms.ImageField(required=False)
    genres = TreeNodeMultipleChoiceField(queryset=Genre.objects.all(), required=True, widget=CheckboxSelectMultiple)
    publication_date = forms.IntegerField(min_value=1900, max_value=timezone.now, required=False,
                                          label='Год издания', help_text='ГГГГ')
    page_count = forms.IntegerField(min_value=1, max_value=5000, required=False, label='Количество страниц')
    price = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=True, label='Стоимость')
    price_per_day = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=True,
                                       label='Цена за день использования')
    instance_count = forms.IntegerField(min_value=1, initial=1, required=True, label='Количество экземпляров')


class AddBookInstanceForm(forms.Form):
    price = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=True, label='Стоимость')
    price_per_day = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=True,
                                       label='Цена за день использования')
    instance_count = forms.IntegerField(min_value=1, max_value=100, initial=1, required=True,
                                        label='Количество экземпляров')
