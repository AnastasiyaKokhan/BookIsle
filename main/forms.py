from django import forms


class BookInstanceForm(forms.Form):
    price = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=True, label='Стоимость*')
    price_per_day = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=True,
                                       label='Цена за день использования*')
    instance_count = forms.IntegerField(min_value=1, max_value=100, initial=1, required=True,
                                        label='Количество экземпляров*')
