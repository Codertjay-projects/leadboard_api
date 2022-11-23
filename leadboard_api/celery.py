import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leadboard_api.settings')

# used redis for saving task and running task
app = Celery('leadboard_api', broker=config("CELERY_BROKER_URL"), backend=config("CELERY_BROKER_URL"))
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.conf.broker_url = config("CELERY_BROKER_URL")

#  this is used to make an automation either send mail during a specific time
#  or delete some stuff or more
app.conf.beat_schedule = {
    # Resend failed mails in 10 minutes
    'send-queued-mail': {
        'task': 'post_office.tasks.send_queued_mail',
        'schedule': 600.0,
    },
    #  This schedule and sends an email to the leads connected to the email_to in the model
    "send_schedule_group_email": {
        "task": 'companies.tasks.send_schedule_group_email',
        "schedule": crontab(hour=1),
    },
    "send_schedule_custom_email": {
        "task": 'companies.tasks.send_schedule_custom_email',
        "schedule": crontab(hour=1),
    },

}


@app.task
def debug_task():
    print(f'Request: ')
