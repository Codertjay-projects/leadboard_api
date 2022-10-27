import uuid

from django.db import models

from companies.models import Group, Company
# Create your models here.
from feedbacks.models import Feedback
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


class LeadContact(models.Model):
    """
    This enables creating leads to enable communication with clients
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    prefix = models.CharField(max_length=50, blank=True, null=True, help_text="Mr, Mrs, Dr etc.")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name="lead_groups", blank=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="staffs")
    last_name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    email = models.EmailField()
    mobile = models.CharField(max_length=250)
    lead_source = models.CharField(choices=LEAD_SOURCE, max_length=250)
    assigned_marketer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                          related_name="assigned_marketers")
    verified = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER, max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY)
    timestamp = models.DateTimeField(auto_now_add=True)

    def previous_feedback(self):
        return Feedback.objects.filter(object_id=self.id).first()
