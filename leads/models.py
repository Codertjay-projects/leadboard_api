import uuid

from django.db import models
from django.utils import timezone

from companies.models import Group, Company
# Create your models here.
from feedbacks.models import Feedback
from users.models import User
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

LEAD_SOURCE = (
    ("SKILLS_APP", "SKILLS_APP"),
    ("WHATSAPP", "WHATSAPP"),
    ("GOOGLE", "GOOGLE"),
    ("BLOG", "BLOG"),
    ("FACEBOOK", "FACEBOOK"),
    ("FRIENDS", "FRIENDS"),
    ("WEBINAR", "WEBINAR"),
    ("NEWS", "NEWS"),
    ("OTHERS", "OTHERS"),
)

GENDER = (
    ("MALE", "MALE"),
    ("FEMALE", "FEMALE"),
    ("OTHERS", "OTHERS")
)
CATEGORY = (
    ("NOT_AWARE", "NOT_AWARE"),
    ("PROBLEM_AWARE", "PROBLEM_AWARE"),
    ("INFORMATION", "INFORMATION"),
    ("BUYING_NOW", "BUYING_NOW"),
)
WANT = (
    ("CHILD", "CHILD"),
    ("SIBLING", "SIBLING"),
    ("SELF", "SELF"),
    ("CHILD_AND_SELF", "CHILD_AND_SELF"),
)
LEAD_TYPE_CHOICES = (
    ("CONTACT_US", "Contact Us"),
    ("HIGH_VALUE_CONTENT", "High Value Content"),
)


class CustomLeadManager(models.Manager):
    def actioned(self, c_id):
        queryset = self.all()
        for instance in queryset:
            instance_id = instance.pk
            print('<><>: ', instance_id)
            print(Feedback.objects.filter(object_id=instance_id, company__id=c_id).count())
            if Feedback.objects.filter(object_id=instance_id, company__id=c_id).count():
                return self.all()
            else:
                return None

    def filter_by_actions(self, company, action_type):
        """
        this is used to filter base on the action provided
        :param company: The company instance
        :param action_type:
        :return:
        """
        Feedback.objects.filter(content_type=ContentType.objects.get_for_model(LeadContact))

        if action_type == "ACTIONED":
            lead_contact_qs = [lead_contact.id for lead_contact in self.filter(company=company) if
                               lead_contact.previous_feedback()]
            return self.filter(id__in=lead_contact_qs)

        elif action_type == "UN-ACTIONED":
            lead_contact_qs = [lead_contact.id for lead_contact in self.filter(company=company) if
                               not lead_contact.previous_feedback()]
            return self.filter(id__in=lead_contact_qs)

        elif action_type == "SCHEDULED":
            lead_contact_qs = [lead_contact.id for lead_contact in self.filter(company=company) if
                               lead_contact.has_scheduled()]
            return self.filter(id__in=lead_contact_qs)
        return self.filter(company=company)


class LeadContact(models.Model):
    """
    This enables creating leads to enable communication with clients
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    prefix = models.CharField(max_length=50, blank=True, null=True, help_text="Mr, Mrs, Dr etc.")
    lead_type = models.CharField(max_length=250, blank=True, null=True, choices=LEAD_TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="lead_companies")
    groups = models.ManyToManyField(Group, related_name="lead_groups", blank=True)
    last_name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    thumbnail = models.ImageField(upload_to="lead_thumbnail", blank=True, null=True)

    middle_name = models.CharField(max_length=250, blank=True, null=True)
    job_title = models.CharField(max_length=250, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    want = models.CharField(max_length=15, choices=WANT, help_text="Who want to learn", blank=True, null=True)
    email = models.EmailField()
    mobile = models.CharField(max_length=250)
    lead_source = models.CharField(choices=LEAD_SOURCE, max_length=250, default="OTHERS")
    assigned_marketer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                          related_name="assigned_marketers")
    is_safe = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    paying = models.BooleanField(default=False)
    send_email = models.BooleanField(null=True)
    gender = models.CharField(choices=GENDER, max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = CustomLeadManager()

    class Meta:
        ordering = ["-timestamp"]

    def previous_feedback(self):
        # Get the last feedback
        return Feedback.objects.filter(object_id=self.id).first()

    def has_scheduled(self):
        # Get the leads that has last scheduled
        last_feed_back = self.previous_feedback()
        if last_feed_back:
            # Check if the last feedback exist
            if last_feed_back.next_schedule > timezone.now():
                return True
        return False

    def all_previous_feedbacks(self):
        # Get all feedbacks made by this user
        return Feedback.objects.filter(object_id=self.id)
