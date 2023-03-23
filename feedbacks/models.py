import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from companies.models import Company
from users.models import User

ACTION_CHOICES = (
    ("MOBILE-CALL", "MOBILE-CALL"),
    ("EMAIL", "EMAIL"),
    ("SMS", "SMS"),
    ("WHATSAPP", "WHATSAPP"),
    ("ZOOM", "Zoom"),
    ("GOOGLE-MEET", "GOOGLE-MEET")
)


class Feedback(models.Model):
    """
    this enables adding info about a schedule or lead meeting which was successful or not

    I am currently using content_type which enables me to use dynamic foreign keys
     to the user-schedule or the lead contact
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    next_schedule = models.DateTimeField(blank=True, null=True)
    feedback = models.CharField(max_length=20000)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
