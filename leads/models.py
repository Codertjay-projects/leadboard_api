import uuid

from django.db import models

# Create your models here.
from users.models import User, Company


class LeadGroup(models.Model):
    Company = models.ForeignKey(Company, related_name="company", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, null=False, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


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
    group = models.ManyToManyField(LeadGroup, related_name="groups", blank=True)
    Company = models.ForeignKey(Company, related_name="company", on_delete=models.CASCADE)
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL)
    last_name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    email = models.EmailField()
    mobile = models.CharField(max_length=250)
    lead_source = models.CharField(choices=LEAD_SOURCE)
    assigned_marketer = models.ForeignKey(User, on_delete=models.SET_NULL)
    verified = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER, max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY)
    timestamp = models.DateTimeField(auto_now_add=True)
