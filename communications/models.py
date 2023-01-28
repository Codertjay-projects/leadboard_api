import uuid

from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from companies.models import Group, Company
from email_logs.models import EmailLog
from .utils import check_email, append_links_and_id_to_description, modify_names_on_description

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
    view_count = models.IntegerField(default=0)
    links_clicked = models.TextField(blank=True, null=True)
    links_clicked_count = models.IntegerField(default=0)
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
        # Create the EmailLog which once created sends an email
        email_log, created = EmailLog.objects.get_or_create(
            company=instance.company,
            message_id=instance.id,
            message_type="CUSTOM",
            email_to=instance.email,
            email_from=instance.company.name,
            email_subject=email_scheduler.email_subject,
            description=description,
            reply_to=instance.company.customer_support_email,
            scheduled_date=email_scheduler.scheduled_date
        )


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
        # remove duplicate emails
        return list(dict.fromkeys(custom_email_list))


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
    links_clicked_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    status = models.CharField(choices=EMAIL_STATUS, max_length=50, default="PENDING", blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)


def post_save_send_group_email_from_log(sender, instance, *args, **kwargs):
    # This creates a task on celery and sends an email on the scheduled time
    if instance.send_groups_email_scheduler.email_to.count() > 0:
        # if the groups is  set because an instance is created before adding the many-to-many field
        if instance.status == "PENDING" or instance.status == "FAILED":
            # The task to send the mail
            # Update the description and append redirect url to all links which enables us to know links clicked
            description = append_links_and_id_to_description(
                description=instance.send_groups_email_scheduler.description,
                email_id=instance.id,
                email_type="group"
            )
            # modify the names on the description
            description = modify_names_on_description(description, instance.first_name, instance.last_name)

            # Create the EmailLog which once created sends an email
            email_log, created = EmailLog.objects.get_or_create(
                company=instance.company,
                message_id=instance.id,
                message_type="GROUP",
                email_to=instance.email,
                email_from=instance.company.name,
                email_subject=instance.send_groups_email_scheduler.email_subject,
                description=description,
                reply_to=instance.company.customer_support_email,
                scheduled_date=instance.send_groups_email_scheduler.scheduled_date
            )


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
        value_list_info = LeadContact.objects.filter(
            company=self.company,
            groups__in=self.email_to.all()).distinct().values_list(
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
