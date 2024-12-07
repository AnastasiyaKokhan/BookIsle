from django.utils import timezone

from django import forms


class BookReturnForm(forms.Form):
    STARS = {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
    }
    return_date = forms.DateField(initial=timezone.now, label='Дата возврата*', widget=forms.SelectDateWidget)
    damage_description = forms.CharField(required=False, label='Описание повреждений', widget=forms.Textarea)
    photo1 = forms.ImageField(required=False)
    photo2 = forms.ImageField(required=False)
    fine_for_damage = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=False,
                                         label='Штраф за повреждение книги')
    changed_price = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=False,
                                       label='Изменить цену')
    reader_assessment = forms.ChoiceField(choices=STARS, required=False, label='Оценка читателя',
                                          widget=forms.RadioSelect)
    changed_rental_cost = forms.DecimalField(min_value=0.01, max_digits=6, decimal_places=2, required=False,
                                             label='Изменить стоимость проката для последующих читателей')
