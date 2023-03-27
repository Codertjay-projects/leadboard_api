from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.utils import timezone

from communications.models import SendEmailScheduler
from companies.models import Company
from email_logs.tasks import leadboard_send_mail
from email_logs.utils import get_email_to

MESSAGE_TYPE = (
    ("CUSTOM", "CUSTOM"),
    ("LEAD_GROUP", "LEAD_GROUP"),
    ("SCHEDULE_GROUP", "SCHEDULE_GROUP"),
    ("HIGHVALUECONTENT", "HIGHVALUECONTENT"),
    ("CAREER", "CAREER"),
    ("EVENT", "EVENT"),
    ("SCHEDULE", "EVENT"),
    ("ALL", "ALL"),
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
    message_type = models.CharField(max_length=250, choices=MESSAGE_TYPE)

    scheduler = models.ForeignKey(SendEmailScheduler, on_delete=models.CASCADE,
                                  related_name='scheduler_instance',
                                  blank=True, null=True
                                  )
    # if we are not sending to lead contact or event register  we send to the email
    email = models.EmailField(blank=True, null=True)

    email_to = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="email_to_instance", blank=True,
                                 null=True)
    # this cant be null but since i am adding it to the model late it has to be null for error issues
    email_to_instance_id = models.UUIDField(blank=True, null=True)
    email_to_content_object = GenericForeignKey('email_to', 'email_to_instance_id')

    max_retries = models.IntegerField(default=0)
    error = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="PENDING")

    #  adding this custom fields which could be used
    view_count = models.IntegerField(default=0)
    links_clicked = models.TextField(blank=True, null=True)
    links_clicked_count = models.IntegerField(default=0)

    timestamp = models.DateTimeField(default=timezone.now)


def post_save_send_email_log(sender, instance: EmailLog, *args, **kwargs):
    """
    This custom function enables us to send email after saving on an appointed time
    """
    if instance.status == "PENDING" or instance.status == "FAILED":
        # the number of times we could try sending the email
        if instance.max_retries < 5:
            # Setting the schedule_time
            scheduled_date = instance.scheduler.scheduled_date
            # if the time has passed I just use the current time
            if scheduled_date <= timezone.now():
                scheduled_date = timezone.now()

            # send the email if its to grou
            # this filter and get the lead contact with the id provided
            email_to_instance = get_email_to(instance.message_type, instance.email_to_instance_id, instance.email)
            # the email to instance can be an email normal email or a lead_contact_instance, schedule_contact_interface
            #  or event_register_instance
            if email_to_instance:
                leadboard_send_mail.apply_async(
                    args=[instance.id,
                          instance.company.name,
                          email_to_instance,
                          instance.company.reply_to_email,
                          instance.scheduler.email_subject,
                          instance.scheduler.description,
                          instance.message_type
                          ],
                    eta=scheduled_date)


post_save.connect(post_save_send_email_log, sender=EmailLog)
