from datetime import datetime

from celery import shared_task
from django.core.mail import send_mail

from config import settings
from .models import Order


@shared_task
def send_overdue_loan_reminders():
    orders = Order.objects.all()
    mails_sent = 0
    for order in orders:
        today = datetime.now()
        issue_date = datetime.combine(order.issue_date, datetime.min.time())
        days_of_use = today - issue_date
        total_price = 0
        total_quantity = order.orderitem_set.all().count()
        fine = 0
        for book in order.orderitem_set.all():
            book_price = book.book_instance.price_per_day * days_of_use.days
            total_price += round(float(book_price), 2)
        if total_quantity > 4:
            total_price *= 0.85
        elif total_quantity > 2:
            total_price *= 0.9
        if days_of_use.days > 30:
            delay_period = days_of_use.days - 30
            fine = round((total_price * 0.01) * delay_period, 2)
            total_price += fine
        if order.return_date == today.date():
            subject = f'Заказ {order.id}'
            message = (f'Уважаемый(ая) {order.reader.username}, срок чтения книг истекает сегодня.'
                       f'За каждый просроченный день взымается пеня в сумме 1% от стоимости заказа.')
            email = [order.reader.email]
            mails_sent += send_mail(subject, message, settings.EMAIL_HOST_USER, email)
        if days_of_use.days >= 35:
            subject = f'Заказ {order.id}'
            message = (f'Уважаемый(ая) {order.reader.username}, срок чтения книг истек {order.return_date}. '
                       f'За каждый просроченный день взымается пеня в сумме 1% от стоимости заказа. '
                       f'Сумма штрафа: {fine}.')
            email = [order.reader.email]
            mails_sent += send_mail(subject, message, settings.EMAIL_HOST_USER, email)
    return mails_sent
