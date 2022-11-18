import uuid

from django.db import models

# Create your models here.
from django.db.models.signals import pre_save

from companies.models import Company
from users.models import User, GENDER_CHOICES
from users.utils import create_slug


class Event(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField()
    location = models.CharField(max_length=250)
    link_1 = models.URLField(blank=True, null=True)
    link_2 = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to="events")
    tags = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=1000, decimal_places=2, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def event_registers(self):
        """
        this returns list of all individuals that are registered to the event
        """
        return self.eventregister_set.all()


def pre_save_event_receiver(sender, instance, *args, **kwargs):
    # enable creating slug for a  event before it is being saved
    if not instance.slug:
        instance.slug = create_slug(instance, Event)


pre_save.connect(pre_save_event_receiver, sender=Event)


class EventRegister(models.Model):
    """
    this enables us to track list of people that have registered for the event
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField()
    mobile = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=50)
    age_range = models.CharField(max_length=50)
    will_receive_email = models.BooleanField(default=False)
    accept_terms_and_conditions = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
