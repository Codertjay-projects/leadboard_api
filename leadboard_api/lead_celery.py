# Set the default Django settings module for the 'celery' program.
import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leadboard_api.settings')

app = Celery('leadboard_api', broker="redis://localhost:6379", backend="redis://localhost:6379")
# used redis for saving task and running task

app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django apps.
app.autodiscover_tasks()

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_TIMEZONE = 'Africa/Lagos'
app.conf.broker_url = config("CELERY_BROKER_URL")

#  this is used to make an automation either send mail during a specific time
#  or delete some stuff or more
app.conf.beat_schedule = {
    # This modify the companies email sent count to one every first day of the month
    "modify_all_company_send_email_count": {
        "task": 'companies.tasks.modify_all_company_send_email_count',
        "schedule": crontab(day_of_month=1),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
