from django.core.exceptions import ValidationError


def validate_passport_number(passport_number):
    if not passport_number[:1].isalpha() and passport_number[1::8].isdigit():
        raise ValidationError('Номер паспорта должен  соответствовать формату: АА0000000')
