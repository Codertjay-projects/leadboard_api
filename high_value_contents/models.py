from django.db import models
import uuid

# Create your models here.
from django.db.models.signals import pre_save
from django.utils import timezone

from companies.models import Company, Group
from users.models import User
from users.utils import create_slug

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


class HighValueContent(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                   null=True, related_name="created_by")
    last_edit_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                     null=True, related_name="last_edit_by")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, null=False, unique=True)
    description = models.TextField(max_length=500)
    thumbnail = models.FileField(upload_to='downloads', blank=True)
    file = models.FileField(upload_to='downloads', blank=True)
    link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    vimeo_link = models.URLField(blank=True, null=True)
    vimeo_hash_key = models.URLField(blank=True, null=True)
    schedule_link = models.URLField(blank=True)
    last_edit = models.DateTimeField(auto_now=True)
    upload_date = models.DateTimeField(default=timezone.now)
    publish = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]


def pre_save_create_high_value_content_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a  schedule_call before it is being saved
    if not instance.slug:
        instance.slug = create_slug(instance, HighValueContent)


pre_save.connect(pre_save_create_high_value_content_receiver, sender=HighValueContent)


class DownloadHighValueContent(models.Model):
    """
    this is used to save the information for the user who wants to download and also after successfully
    created we verify so when the download is verified we then save the information to the lead
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    high_value_content = models.ForeignKey(HighValueContent, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField()
    lead_source = models.CharField(choices=LEAD_SOURCE, max_length=250)
    verified = models.BooleanField(default=False)
    is_safe = models.BooleanField(default=False)
    want = models.CharField(max_length=250)
    on_leadboard = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
