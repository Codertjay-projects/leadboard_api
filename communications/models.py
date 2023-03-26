import uuid

from django.db import models
from django.utils import timezone

from companies.models import Group, Company
from events.models import Event
from high_value_contents.models import HighValueContent
from schedules.models import ScheduleCall
from .utils import check_email

EMAIL_STATUS = (
    ("PENDING", "PENDING"),
    ("SENT", "SENT"),
    ("FAILED", "FAILED"),
)

MESSAGE_TYPE = (
    ("CUSTOM", "CUSTOM"),
    ("LEAD_GROUP", "LEAD_GROUP"),
    ("SCHEDULE_GROUP", "SCHEDULE_GROUP"),
    ("HIGHVALUECONTENT", "HIGHVALUECONTENT"),
    ("CAREER", "CAREER"),
    ("EVENT", "EVENT"),
    ("ALL", "ALL"),
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
    # The schedule call is used for schedules
    schedule_calls = models.ManyToManyField(ScheduleCall, blank=True)
    high_value_contents = models.ManyToManyField(HighValueContent, blank=True)
    #  list of email comma seperated
    email_list = models.TextField(blank=True, null=True)
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
        ).distinct()
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

    def get_schedule_emails(self) -> list:
        """
        This returns a list of emails with dictionary containing leads to get this
        :return: [  {"email": "email@example",
                    "first_name": "Example",
                    "last_name": "Example",
                    "user_schedule_id":"lead_id",
                    "scheduler_id": the_instance_id

                    }...
                    ]
        """
        #  fGet the leads email  that are connected to the SendGroupsEmailScheduler
        #  and also the id of the SendGroupsEmailScheduler
        from schedules.models import UserScheduleCall
        value_list_info = UserScheduleCall.objects.filter(
            company=self.company,
            schedule_call_id__in=self.schedule_calls.all()).distinct().values_list(
            "email",
            "first_name",
            "last_name",
            "id"
        ).distinct()
        schedule_email_list_info = []
        for item in value_list_info:
            # Create a dictionary which enables easy access
            info = {
                "email": item[0],
                "first_name": item[1],
                "last_name": item[2],
                "user_schedule_id": item[3],
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

    def get_all_emails(self):
        """
        this get all emails attached to a company
        :return:
        """
        # I need the flat to be used in here

        company = self.company
        all_company_newsletter_mail = list(company.newsletter_set.all().values_list("email", flat=True))
        # all the people that register for events under the company
        all_company_event_register_email = list(company.eventregister_set.all().values_list("email", flat=True))
        # get all the lead contacts email
        all_company_lead_contacts_email = list(company.lead_companies.all().values_list("email", flat=True))
        # get all company schedule email
        all_company_schedule_email = list(company.userschedulecall_set.all().values_list("email", flat=True))

        unique_list_if_email = list(set(all_company_newsletter_mail + all_company_schedule_email +
                                        all_company_lead_contacts_email + all_company_event_register_email))
        # this makes the email unique
        return unique_list_if_email

    def get_all_high_value_contents(self):
        """
        this returns all the high value contents lead contacts provided
        :return:
        """
        value_list_info = self.high_value_contents.all().values_list(
            "lead_contacts__email",
            "lead_contacts__first_name",
            "lead_contacts__last_name",
            "lead_contacts__id",
        ).distinct()

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
