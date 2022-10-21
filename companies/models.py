import uuid

from django.db import models

# Create your models here.
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


COMPANY_SIZE_CHOICES = (
    ("2-10 Employees", "2-10 Employees"),
)


class Location(models.Model):
    """this contains list of location which could be used for the company """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)


class Company(models.Model):
    """
    This enables identifying what company a user exists in when assigning marketer to a lead
    and also add what part does a user belong to in his company
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=250)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=25)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    overview = models.TextField()
    company_size = models.CharField(choices=COMPANY_SIZE_CHOICES)
    headquater = models.CharField(max_length=250)
    founded = models.DateField()
    location = models.ManyToManyField(Location, blank=True)
    admins = models.ManyToManyField(User, blank=True)
    marketers = models.ManyToManyField(User, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
