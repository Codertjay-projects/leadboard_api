import uuid

from django.db import models

# Create your models here.
from django.utils import timezone

from companies.models import Company, Group


class ContactUs(models.Model):
    """
    The reason why this was created was to manage email under your company .I know we are supposed
    to use the leadboard to save the user email directly and attend to the user but sometimes the
    user might not want to be part.
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
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    message = models.TextField()
    on_leadboard = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    # fixme: when a user unsubscribe and the user is in a lead i remove the group

    class Meta:
        ordering = ["-timestamp"]


class Newsletter(models.Model):
    """
    this is used for users trying to only update from blogs and other information
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    on_blog = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)


class UnSubscriber(models.Model):
    """
    This contains list of info about a user who would like to unsubscribe from the lead
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.EmailField()
    message = models.CharField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now)
