from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.utils import timezone

from companies.models import Company
from email_logs.tasks import leadboard_send_mail

MESSAGE_TYPE = (
    ("CUSTOM", "CUSTOM"),
    ("GROUP", "GROUP"),
    ("HIGHVALUECONTENT", "HIGHVALUECONTENT"),
    ("CAREER", "CAREER"),
    ("EVENT", "EVENT"),
    ("OTHERS", "OTHERS"),
)

EMAIL_LOG_STATUS = (
    ("FAILED", "FAILED"),
    ("PENDING", "PENDING"),
    ("SENT", "SENT"),
)


class EmailLog(models.Model):
    """
    this logs all mails sent , it doesn't check the organisation.
    the reason I created this was to be able to know if a mail was sent successfully
    and if not I can reschedule the mail just like post office which have a lot but i
    need to manage few on my own
    """
    # the message id is an ID from the message we are trying to send
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=250)
    message_type = models.CharField(max_length=250, choices=MESSAGE_TYPE)
    # the email_from example : "instinchub "
    email_from = models.CharField(max_length=250)
    email_to = models.EmailField()
    reply_to = models.EmailField()
    max_retries = models.IntegerField(default=0)
    email_subject = models.CharField(max_length=250)
    description = models.TextField()
    error = models.TextField(blank=True, null=True)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=50, default="PENDING")
    timestamp = models.DateTimeField(default=timezone.now)


def post_save_send_email_log(sender, instance, *args, **kwargs):
    if instance.status == "PENDING" or instance.status == "FAILED":
        # the number of times we could try sending the email
        if instance.max_retries < 5:
            # Setting the schedule_time
            scheduled_date = instance.scheduled_date
            # if the time has passed I just use the current time
            if instance.scheduled_date <= timezone.now():
                scheduled_date = timezone.now()
            leadboard_send_mail(
                instance.message_id,
                instance.company.name,
                instance.email_to,
                instance.reply_to,
                instance.email_subject,
                instance.description
            )
            # leadboard_send_mail.apply_async(
            #     args=[instance.message_id,
            #           instance.company.name,
            #           instance.email_to,
            #           instance.reply_to,
            #           instance.email_subject,
            #           instance.description
            #           ],
            #     eta=scheduled_date)


post_save.connect(post_save_send_email_log, sender=EmailLog)
