# Create your views here.
from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import status
from django.contrib.contenttypes.models import ContentType

from companies.utils import check_marketer_and_admin_access_company, is_valid_uuid
from feedbacks.models import Feedback
from feedbacks.serializers import FeedbackSerializer
from users.permissions import LoggedInPermission
from leads.models import LeadContact, Company
from schedules.models import UserScheduleCall


class LeadContactFeedbackViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = FeedbackSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self, *args, **kwargs):
        # the lead id
        lead_contact_id = self.request.query_params.get("lead_contact_id")
        #  this filter base on the lead id  provided
        if not lead_contact_id:
            raise Http404
        feedback = Feedback.objects.filter(object_id=lead_contact_id)
        return feedback

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  get the lead with the object_id . for verification purposes
        lead_contact = LeadContact.objects.get(id=instance.object_id)
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, lead_contact.company):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  get the lead with the object_id . for verification purposes
        lead_contact = LeadContact.objects.get(id=instance.object_id)
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, lead_contact.company):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)



class FeedbackListView(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    lookup_field = 'pk'


class FeedbackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):

        # Authorization
        company = Company.objects.filter(id=is_valid_uuid(kwargs['c_id'])).first()
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)

        content_type = None
        contact_uuid = is_valid_uuid(request.data['lead_id'])
        if request.data['model_type'] == 'schedules.userschedulecall':
            content_type = ContentType.objects.get_for_model(UserScheduleCall)
        elif request.data['model_type'] == 'leads.leadcontact':
            content_type = ContentType.objects.get_for_model(LeadContact)

        if contact_uuid and content_type:
            if serializer.is_valid(raise_exception=False):
                feedbacks = Feedback(
                    content_type=content_type,
                    object_id=contact_uuid,
                    feedback=request.data['feedback'],
                    action=request.data['action'],
                    staff=self.request.user,
                    company=company
                )
                if request.data['next_schedule']:
                    feedbacks.next_schedule = request.data['next_schedule']
                feedbacks.save()
            feedback_serializer = FeedbackSerializer(feedbacks, partial=True)
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)