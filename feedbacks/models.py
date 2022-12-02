import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from users.models import User

ACTION_CHOICES = (
    ("CALL", "CALL"),
    ("EMAIL", "EMAIL"),
    ("SMS", "SMS"),
    ("WHATSAPP", "WHATSAPP"),
    ("ZOOM", "Zoom"),
    ("GOOGLE-MEET", "GOOGLE-MEET")
)


class FeedbackManager(models.Manager):
    """
    this enables add extra function using the object to access it
    """

    def create_by_model_type(self, model_type, other_model_id, feedback, action, next_schedule, staff):
        """
        this enables creating feedback . In which the feedback has a foreign key
        to . for now the leadcontact  and also the userschedule are both sharing the same feedback
        """
        model_qs = ContentType.objects.filter(model=model_type)
        if model_qs.exists():
            SomeModel = model_qs.first().model_class()
            """ is just like we are getting the first lead or schedule"""
            other_model = SomeModel.objects.filter(id=other_model_id).first()
            #  the other_model is either the lead or the schedule
            if other_model:  # checkin  if the queryset exist
                instance = self.model()
                instance.feedback = feedback
                instance.action = action
                instance.next_schedule = next_schedule
                instance.content_type = model_qs.first()
                instance.staff = staff
                instance.object_id = other_model.id
                instance.save()
                return instance
        return None


class Feedback(models.Model):
    """
    this enables adding info about a schedule or lead meeting which was successful or not

    I am currently using content_type which enables me to use dynamic foreign keys
     to the user-schedule or the lead contact
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    next_schedule = models.DateField(blank=True, null=True)
    feedback = models.CharField(max_length=20000)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = FeedbackManager()

    class Meta:
        ordering = ['-timestamp']
