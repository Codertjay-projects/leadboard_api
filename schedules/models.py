import uuid

from django.db import models

# Create your models here.
from companies.models import Company, Group
from leads.models import GENDER
from users.models import User

USER_TYPE_CHOICE = (
    ("PARENT", "PARENT"),
    ("INDIVIDUAL", "INDIVIDUAL"),
)
WILL_SUBSCRIBE_CHOICES = (
    ("YES", "YES"),
    ("NO", "NO"),
)


class UserScheduleCall(models.Model):
    """
    This enables scheduling calls or meetings with clients from the leads
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    groups = models.ManyToManyField(Group, related_name="user_schedule_groups", blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
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
    user_type = models.CharField(choices=USER_TYPE_CHOICE, max_length=250)
    schedule_call = models.ForeignKey("ScheduleCall", on_delete=models.SET_NULL, blank=True, null=True)
    will_subscribe = models.CharField(max_length=50, choices=WILL_SUBSCRIBE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)


class ScheduleCall(models.Model):
    """
    This contains info about the meeting that is going to take place which is crea
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=250, )
    minutes = models.IntegerField()
    meeting_link = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
