import uuid

from django.db import models
# Create your models here.
from django.db.models.signals import pre_save
from django.utils import timezone

from companies.models import Company, Group
from users.models import User
from users.utils import create_slug

LEAD_SOURCE = (
    ("instincthub", "instinctHub"),
    ("whatsapp", "WHATSAPP"),
    ("google", "GOOGLE"),
    ("blog", "BLOG"),
    ("facebook", "FACEBOOK"),
    ("friends", "FRIENDS"),
    ("webinar", "WEBINAR"),
    ("news", "NEWS"),
    ("others", "OTHERS"),
)


class HighValueContentManager(models.Manager):
    """"
    This is used to create custom function that can be used
    """

    def get_all_downloads_count(self, company: Company) -> int:
        """this returns the total number of people that downloads the high value content"""
        download_count = 0
        high_value_contents = self.filter(company=company)
        for item in high_value_contents:
            download_count += item.lead_contacts.count()
        return download_count


class HighValueContent(models.Model):
    """"
    This contains list of high value content that can be shared and downloaded
    """
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
    # lead contacts which are the list of people that have downloaded the  high value content
    lead_contacts = models.ManyToManyField("leads.LeadContact", blank=True)

    timestamp = models.DateTimeField(default=timezone.now)

    objects = HighValueContentManager()

    class Meta:
        ordering = ["-timestamp"]


def pre_save_create_high_value_content_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a  schedule_call before it is being saved
    if not instance.slug:
        instance.slug = create_slug(instance, HighValueContent)


pre_save.connect(pre_save_create_high_value_content_receiver, sender=HighValueContent)
