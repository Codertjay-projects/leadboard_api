import uuid

from django.db import models

# Create your models here.
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


ACTION_CHOICES = (
    ("CALL", "CALL"),
    ("EMAIL", "EMAIL"),
    ("SMS", "SMS"),
    ("WHATSAPP", "WHATSAPP"),
    ("ZOOM", "Zoom"),
    ("GOOGLE-MEET", "GOOGLE-MEET")
)


class FeedBack(models.Model):
    """
    this enables feedback enables adding info about how the lead call or meeting went
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL)
    lead_contact = models.ForeignKey(LeadContact, on_delete=models.SET_NULL)
    user_schedule_call = models.ForeignKey("UserScheduleCall", on_delete=models.SET_NULL)
    next_schedule = models.DateField(blank=True, null=True)
    feedback = models.CharField(max_length=20000)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)


USER_TYPE_CHOICE = (
    ("PARENT", "PARENT"),
    ("INDIVIDUAL", "INDIVIDUAL"),
)


class UserScheduleCall(models.Model):
    """
    This enables scheduling calls or meetings with clients from the leads
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    phone = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDER, max_length=50)
    age = models.IntegerField(blank=True, null=True)
    schedule_date = models.DateField()
    schedule_time = models.TimeField()
    location = models.CharField(max_length=250)
    have_laptop = models.BooleanField(default=False)
    good_internet = models.BooleanField(default=False)
    weekly_commitment = models.CharField(max_length=250)
    saturday_check_in = models.CharField(max_length=50)
    user_type = models.BooleanField(choices=USER_TYPE_CHOICE)
    schedule_call = models.ForeignKey("ScheduleCall", on_delete=models.SET_NULL)


class ScheduleCall(models.Model):
    """
    This contains info about the meeting that is gonna take place which is crea
    """
