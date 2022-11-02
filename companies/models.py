import uuid

from django.db import models

# Create your models here.
from django.db.models.signals import pre_save
from django.utils.text import slugify

from users.models import User


class Industry(models.Model):
    """
    these are the list of the industries in which a company can choose
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


COMPANY_SIZE_CHOICES = (
    ("2-10", "2-10"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("201-500", "201-500"),
    ("501-1000", "501-1000"),
    ("1001-5000", "1001-5000"),
    ("5001-10000", "5001-10000"),
    ("10000-+", "10000-+"),
)


class Location(models.Model):
    """this contains list of location which could be used for the company """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class Company(models.Model):
    """
    This enables identifying what company a user exists in when assigning marketer to a lead
    and also add what part does a user belong to in his company
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=250)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=25)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    overview = models.TextField()
    company_size = models.CharField(choices=COMPANY_SIZE_CHOICES, max_length=250)
    headquater = models.CharField(max_length=250)
    founded = models.DateField()
    locations = models.ManyToManyField(Location, blank=True)
    admins = models.ManyToManyField(User, blank=True, related_name="admins")
    marketers = models.ManyToManyField(User, blank=True, related_name="marketers")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class Group(models.Model):
    """
    This contains list of activities on a companies in which the company uses to group
    his or her leads or meeting schedules
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, null=False, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.title


def pre_save_group_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a  group before it is being saved
    # todo: calculate blog read time
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_group_receiver, sender=Group)


def create_slug(instance, new_slug=None):
    """
    This creates a slug for a group   before it is being
     saved and if the slug exist it add the id the old group  to the slug
    :param instance: group
    :param new_slug: slug passed if existed
    :return: slug
    """
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Group.objects.filter(slug=slug).order_by('-id')
    if qs.exists():
        new_slug = f'{slug}-{qs.first().id}'
        return create_slug(instance, new_slug=new_slug)
    return slug
