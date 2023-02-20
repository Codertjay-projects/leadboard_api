# Create your views here.
from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import status

from companies.utils import check_marketer_and_admin_access_company
from feedbacks.models import Feedback
from feedbacks.serializers import FeedbackSerializer
from users.permissions import LoggedInPermission
from leads.models import LeadContact, Company


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
        company = Company.objects.filter(id=kwargs['c_id']).first()
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid(raise_exception=False):
            # print(request.data)


            feedback = Feedback.objects.create_by_model_type(
                model_type="leadcontact",
                other_model_id=request.data['lead_id'],
                feedback=request.data['feedback'],
                action=request.data['action'],
                next_schedule=request.data['next_schedule'],
                staff=self.request.user,
                company=company
            )

            feedback_data = FeedbackSerializer(feedback, partial=True)

            # serializer.save()
            # Return custom response
            return Response(feedback_data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)