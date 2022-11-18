import uuid

from django.db import models
from django.db.models.signals import pre_save

from companies.models import Company, Group
from feedbacks.models import Feedback
from leads.models import GENDER, LeadContact
from users.models import User
from users.utils import create_slug

USER_TYPE_CHOICE = (
    ("PARENT", "PARENT"),
    ("INDIVIDUAL", "INDIVIDUAL"),
)
WILL_SUBSCRIBE_CHOICES = (
    ("YES", "YES"),
    ("NO", "NO"),
)
COMMUNICATION_MEDIUM = (
    ("CALL", "CALL"),
    ("EMAIL", "EMAIL"),
    ("SMS", "SMS"),
    ("WHATSAPP", "WHATSAPP"),
    ("ZOOM", "Zoom"),
    ("GOOGLE-MEET", "GOOGLE-MEET")
)
AGE_RANGE = (
    ("18-24", "18-24"),
    ("25-30", "25-30"),
    ("31-35", "31-35"),
    ("36-40", "36-40"),
    ("41+", "41+"),
)


class UserScheduleCall(models.Model):
    """
    This enables scheduling calls or meetings with clients from the leads
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name="user_schedule_groups", blank=True)
    assigned_marketer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    age_range = models.CharField(max_length=5, blank=True, null=True, choices=AGE_RANGE)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=250)
    gender = models.CharField(choices=GENDER, max_length=50)
    phone = models.CharField(max_length=50)
    age = models.IntegerField(blank=True, null=True)
    communication_medium = models.CharField(choices=COMMUNICATION_MEDIUM, max_length=250)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    employed = models.BooleanField(blank=True, null=True)
    other_training = models.BooleanField(blank=True, null=True)
    other_training_lesson = models.CharField(max_length=200, blank=True, null=True)
    will_pay = models.BooleanField(blank=True, null=True, help_text="Willing to invest in learning financially?")
    income_range = models.CharField(max_length=200, blank=True, null=True, help_text="Monthly income range.")
    knowledge_scale = models.IntegerField(blank=True, null=True)
    have_laptop = models.BooleanField(blank=True, null=True)
    will_get_laptop = models.BooleanField(blank=True, null=True)
    when_get_laptop = models.CharField(max_length=200, blank=True, null=True)
    good_internet = models.BooleanField(blank=True, null=True)
    weekly_commitment = models.CharField(max_length=50, blank=True, null=True)
    saturday_check_in = models.BooleanField(blank=True, null=True)
    hours_per_week = models.CharField(max_length=20)
    catch_up_per_hours_weeks = models.CharField(max_length=20, blank=True, null=True)
    more_details = models.TextField(blank=True, null=True)
    kids_count = models.IntegerField(blank=True, null=True)
    kids_years = models.CharField(max_length=100, blank=True, null=True)
    time_close_from_school = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICE, blank=True, null=True)
    schedule_call = models.ForeignKey("ScheduleCall", on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='schedule_calls')
    lead_contact = models.ForeignKey(LeadContact, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='lead_contacts')
    eligible = models.BooleanField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def previous_feedback(self):
        return Feedback.objects.filter(object_id=self.id).first()


class ScheduleCall(models.Model):
    """
    This contains info about the meeting that is going to take place which is crea
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=250, )
    slug = models.SlugField(unique=True)
    minutes = models.IntegerField()
    meeting_link = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


def pre_save_schedule_call_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a  schedule_call before it is being saved
    if not instance.slug:
        instance.slug = create_slug(instance, ScheduleCall)


pre_save.connect(pre_save_schedule_call_receiver, sender=ScheduleCall)
