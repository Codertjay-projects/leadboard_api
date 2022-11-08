import uuid

from django.db import models

# Create your models here.
from django.utils import timezone

from companies.models import Company, Group


class CompanySubscriber(models.Model):
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
    subscribed = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)
    # fixme: when a user unsubscribe and the user is in a lead i remove the group


    class Meta:
        ordering = ["-timestamp"]
