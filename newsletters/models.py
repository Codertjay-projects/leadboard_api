import uuid

from django.db import models

# Create your models here.
from django.utils import timezone

from companies.models import Company, Group


class CompanySubscriber(models.Model):
    """
    this company subscribers enables users to subscribe to a particular group under a company .
    so it enables us to manage all users in that are subscribed to the company
      : this is used for filtering base on the staff loggedin trying to send an automated message
    that way we would know the user has access sending mail to this users
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    email = models.EmailField()
    subscribed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
