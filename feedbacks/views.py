from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet

from feedbacks.models import Feedback
from feedbacks.serializers import FeedbackSerializer
from users.permissions import LoggedInPermission


class LeadContactFeedbackViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = FeedbackSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        # the lead id
        lead_contact_id = self.GET.get("lead_contact_id")
        #  this filter base on the lead id  provided
        feedback = Feedback.objects.filter(object_id=lead_contact_id)
        return feedback
