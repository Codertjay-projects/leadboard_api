import uuid

from django.db import models

from companies.models import Group, Company
# Create your models here.
from feedbacks.models import Feedback
from high_value_contents.models import HighValueContent
from users.models import User

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
    ("CONTACTUS", "CONTACTUS"),
    ("HIGHVALUECONTENT", "HIGHVALUECONTENT"),
)


class LeadContact(models.Model):
    """
    This enables creating leads to enable communication with clients
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    prefix = models.CharField(max_length=50, blank=True, null=True, help_text="Mr, Mrs, Dr etc.")
    lead_type = models.CharField(max_length=250, blank=True, null=True, choices=LEAD_TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
    gender = models.CharField(choices=GENDER, max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # fixme : custom fields

    class Meta:
        ordering = ["-timestamp"]

    def previous_feedback(self):
        # Get the last feedback
        return Feedback.objects.filter(object_id=self.id).first()

    def all_previous_feedbacks(self):
        # Get all feedbacks made by this user
        return Feedback.objects.filter(object_id=self.id)
