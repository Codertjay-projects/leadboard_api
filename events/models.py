import uuid

from django.db import models

# Create your models here.
from companies.models import Company
from users.models import User


class Event(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    title = models.CharField(max_length=250)
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
