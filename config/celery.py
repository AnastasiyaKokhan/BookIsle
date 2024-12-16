import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config', broker='pyamqp://guest:guest@localhost//')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send-overdue-loan-reminders-every-day': {
        'task': 'orders.tasks.send_overdue_loan_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
}
