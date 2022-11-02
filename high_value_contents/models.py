from django.db import models
import uuid

# Create your models here.
from companies.models import Company, Group


class HighValueContent(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    # fixme: add auto delete  when file get deleted
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    file = models.FileField(null=True, blank=True, upload_to="storages")
    link_1 = models.URLField(null=True, blank=True)
    link_2 = models.URLField(null=True, blank=True)
    link_3 = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
