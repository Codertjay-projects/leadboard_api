import uuid

from django.db import models
from django.utils import timezone

from companies.models import Group, Company
from events.models import Event
from .utils import check_email

EMAIL_STATUS = (
    ("PENDING", "PENDING"),
    ("SENT", "SENT"),
    ("FAILED", "FAILED"),
)

MESSAGE_TYPE = (
    ("CUSTOM", "CUSTOM"),
    ("GROUP", "GROUP"),
    ("HIGHVALUECONTENT", "HIGHVALUECONTENT"),
    ("CAREER", "CAREER"),
    ("EVENT", "EVENT"),
    ("OTHERS", "OTHERS"),
)


class SendEmailScheduler(models.Model):
    """
    This is used to send am email to list of groups users on the lead.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    message_type = models.CharField(max_length=250, blank=True, null=True, choices=MESSAGE_TYPE)

    # the set of groups the email is sent to it could be from  newsletters, contacts,downloads and schedule
    groups = models.ManyToManyField(Group, blank=True)
    events = models.ManyToManyField(Event, blank=True)
    #  list of email comma seperated
    email_list = models.TextField()
    email_subject = models.CharField(max_length=250)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(max_length=1500)
    timestamp = models.DateTimeField(default=timezone.now)

    def get_lead_emails(self) -> list:
        """
        This returns a list of emails with dictionary containing leads to get this
        :return: [  {"email": "email@example",
                    "first_name": "Example",
                    "last_name": "Example",
                    "lead_contact_id":"lead_id",
                    "scheduler_id": the_instance_id

                    }...
                    ]
        """
        #  Get the leads email  that are connected to the SendGroupsEmailScheduler
        #  and also the id of the SendGroupsEmailScheduler
        from leads.models import LeadContact
        value_list_info = LeadContact.objects.filter(
            company=self.company,
            groups__in=self.groups.all()).distinct().values_list(
            "email",
            "first_name",
            "last_name",
            "id"
        )
        schedule_email_list_info = []
        for item in value_list_info:
            # Create a dictionary which enables easy access
            info = {
                "email": item[0],
                "first_name": item[1],
                "last_name": item[2],
                "lead_contact_id": item[3],
                "scheduler_id": self.id
            }
            schedule_email_list_info.append(info)
        return schedule_email_list_info

    def get_events_email(self):
        """
        this is used to get the events emails of the people that registered
        :return: [
        {
        "email":email",
        "first_name":firstname",
        "last_name":"last_name,
        "event_register_id":event_register_id,
        "scheduler_id": the_instance_id

        }
        ]
        """
        # get the event model
        from events.models import Event, EventRegister
        event_registers_info = EventRegister.objects.filter(
            event__in=self.events.all()
        ).distinct().values_list(
            "email",
            "first_name",
            "last_name",
            "id",
        )
        schedule_email_list_info = []
        for item in event_registers_info:
            # Create a dictionary which enables easy access
            info = {
                "email": item[0],
                "first_name": item[1],
                "last_name": item[2],
                "event_id": item[3],
                "scheduler_id": self.id
            }
            schedule_email_list_info.append(info)
        return schedule_email_list_info

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
