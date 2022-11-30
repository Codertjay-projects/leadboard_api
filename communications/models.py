import uuid

from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from companies.models import Group, Company
from .tasks import send_email_group_schedule_task, send_email_custom_schedule_task
from .utils import check_email, append_links_and_id_to_description

EMAIL_STATUS = (
    ("PENDING", "PENDING"),
    ("SENT", "SENT"),
    ("FAILED", "FAILED"),
)


class SendCustomEmailSchedulerLog(models.Model):
    """"
    this is used to log SendCustomEmailScheduler from the email_list provided
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    send_custom_email_scheduler = models.ForeignKey("SendCustomEmailScheduler", on_delete=models.CASCADE)
    email = models.EmailField()
    status = models.CharField(max_length=250, choices=EMAIL_STATUS, default="PENDING")
    emails_view_count = models.IntegerField(default=0)
    sent_mail_count = models.IntegerField(default=0)
    read_mail_count = models.IntegerField(default=0)
    links_clicked = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)


def post_save_send_custom_email_from_log(sender, instance, *args, **kwargs):
    """
    Once the email is saved to the database
    """
    if instance.status == "PENDING" or instance.status == "FAILED":
        # if the instance is pending or failed we re-schedule the email
        email_scheduler = instance.send_custom_email_scheduler
        # Update the description and append redirect url to all links which enables us to know links clicked
        description = append_links_and_id_to_description(
            description=email_scheduler.description,
            email_id=instance.id,
            email_type="custom"
        )
        send_email_custom_schedule_task.delay(
            to_email=instance.email,
            subject=email_scheduler.email_subject,
            reply_to=instance.company.customer_support_email,
            description=description,
            scheduled_date=email_scheduler.scheduled_date,
            company_info_email=instance.company.info_email,
            company_name=instance.company.name,
            email_id=instance.id,
        )
        instance.status = "SENT"


post_save.connect(post_save_send_custom_email_from_log, sender=SendCustomEmailSchedulerLog)


class SendCustomEmailScheduler(models.Model):
    """
    This is used to send custom mail email message to users passed in text comma seperated
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email_subject = models.CharField(max_length=250)
    #  list of email comma seperated
    email_list = models.TextField()
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    timestamp = models.DateTimeField(default=timezone.now)

    def get_custom_emails(self) -> list:
        """
        this returns a list of emails gotten from the email_list
        which is a text field
        :return: ["easy@mail.com","easy@mail.com","easy@mail.com"]
        """
        custom_email_list = self.email_list.split(",")
        for item in custom_email_list:
            # Validate the email
            if not check_email(item):
                # remove the email from the list if not value
                custom_email_list.remove(item)
        return custom_email_list


def post_save_create_send_custom_email_log(sender, instance, *args, **kwargs):
    """"
    This creates a custom email log for the custom email that was added and the user is willing to send
    """
    if instance.get_custom_emails():
        for item in instance.get_custom_emails():
            send_custom_email_scheduler, created = SendCustomEmailSchedulerLog.objects.get_or_create(
                email=item,
                company=instance.company,
                send_custom_email_scheduler=instance,
            )


post_save.connect(post_save_create_send_custom_email_log, sender=SendCustomEmailScheduler)


####################################################################################################
# Group Email Starts Here below ⏬⏬⏬
####################################################################################################

class SendGroupsEmailSchedulerLog(models.Model):
    """
    This is used to log the emails sent by the SendGroupsEmailScheduler
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    send_groups_email_scheduler = models.ForeignKey("SendGroupsEmailScheduler", on_delete=models.CASCADE)
    # the emails would be unique with this SendGroupsEmailScheduler so on create I send the email with post_office
    email = models.EmailField()
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    links_clicked = models.TextField(blank=True, null=True)
    status = models.CharField(choices=EMAIL_STATUS, max_length=50, default="PENDING", blank=True, null=True)
    emails_view_count = models.IntegerField(default=0)
    sent_mail_count = models.IntegerField(default=0)
    read_mail_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)


def post_save_send_group_email_from_log(sender, instance, *args, **kwargs):
    # This creates a task on celery and sends an email on the scheduled time
    if instance.status == "PENDING" or instance.status == "FAILED":
        # The task to send the mail
        # Update the description and append redirect url to all links which enables us to know links clicked
        description = append_links_and_id_to_description(
            description=instance.send_groups_email_scheduler.description,
            email_id=instance.id,
            email_type="custom"
        )
        send_email_group_schedule_task.delay(
            to_email=instance.email,
            subject=instance.send_groups_email_scheduler.email_subject,
            reply_to=instance.company.customer_support_email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            description=description,
            scheduled_date=instance.send_groups_email_scheduler.scheduled_date,
            company_info_email=instance.company.info_email,
            company_name=instance.company.name,
            email_id=instance.id,
        )
        # Set the status to sent
        instance.status = "SENT"


post_save.connect(post_save_send_group_email_from_log, sender=SendGroupsEmailSchedulerLog)


class SendGroupsEmailScheduler(models.Model):
    """
    This is used to send am email to list of groups users on the lead.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    # the set of groups the email is sent to it could be from  newsletters, contacts,downloads and schedule
    email_to = models.ManyToManyField(Group, blank=True)
    email_from = models.CharField(max_length=250)
    email_subject = models.CharField(max_length=250)
    scheduled_date = models.DateTimeField()
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def get_lead_emails(self) -> list:
        """
        This returns a list of emails with dictionary containing leads to get this
        :return: [  {"email": "email@example",
                    "first_name": "Example",
                    "last_name": "Example"
                    }...
                    ]
        """
        #  Get the leads email  that are connected to the SendGroupsEmailScheduler
        #  and also the id of the SendGroupsEmailScheduler
        from leads.models import LeadContact
        value_list_info = LeadContact.objects.filter(company=self.company, groups__in=self.email_to.all()).values_list(
            "email",
            "first_name",
            "last_name",
        )
        schedule_email_list_info = []
        for item in value_list_info:
            # Create a dictionary which enables easy access
            info = {
                "email": item[0],
                "first_name": item[1],
                "last_name": item[2],
            }
            schedule_email_list_info.append(info)
        return schedule_email_list_info


def post_save_create_send_group_email_log(sender, instance, *args, **kwargs):
    """
   This creates a log on the SendGroupsEmailSchedulerLog which enables us to get more information about
     the email
    :return:
    """
    if instance.email_to.count() > 0:
        # The email to must be added before sending the email
        pending_mail_info = instance.get_lead_emails()
        for item in pending_mail_info:
            # Try getting to send group email log if it exists before and if it doesn't
            # exist I just add extra fields
            send_group_email_log, created = SendGroupsEmailSchedulerLog.objects.get_or_create(
                email=item.get("email"),
                send_groups_email_scheduler=instance,
                company=instance.company
            )
            if created:
                # Get the first name and last name from the dictionary on the list
                send_group_email_log.first_name = item.get("first_name")
                send_group_email_log.last_name = item.get("last_name")
                send_group_email_log.save()


post_save.connect(post_save_create_send_group_email_log, sender=SendGroupsEmailScheduler)
