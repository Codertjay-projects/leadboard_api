import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from users.models import User

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
    this enables adding info about a schedule or lead meeting which was successful or not

    i am currently using content_type which enables me to use dynamic foreign keys
     to the user-schedule or the lead contact
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    next_schedule = models.DateField(blank=True, null=True)
    feedback = models.CharField(max_length=20000)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
