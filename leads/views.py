from django.http import Http404
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from companies.models import Company
from companies.utils import check_marketer_and_admin_access_company
from feedbacks.models import Feedback
from feedbacks.serializers import FeedbackCreateSerializer, FeedbackSerializer
from .models import LeadContact
from users.permissions import LoggedInPermission
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import LeadContactUpdateCreateSerializer, LeadContactSerializer


class LeadContactCreateListAPIView(ListCreateAPIView):
    """
    This class is meant to list all the lead contact and also create a new one
    """
    permission_classes = [LoggedInPermission]
    serializer_class = LeadContactSerializer

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.kwargs.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        """
        this filter using the company id passed on the urls to get the leads associated with it
        :return:
        """
        lead = self.get_company().leadcontact_set.all()
        return lead

    def create(self, request, *args, **kwargs):
        #  before creating a lead we have to make sure the user is a member of that company
        company = self.get_company()
        #  using the company which enables us to verify if the user has access to create the company
        #  i created this method in the companies/utils.py to enable check if
        #  the user has access to create the lead using the company
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have access to create this lead under this company ."}, status=400)
        serializer = LeadContactUpdateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(staff=self.request.user, company=company)
        return Response(serializer.data, status=201)


class LeadContactRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to update the lead , delete i, and also retrieve the lead .
    Note that once the lead is deleted the feedback connected ti will be deleted
    """
    permission_classes = [LoggedInPermission]
    serializer_class = LeadContactUpdateCreateSerializer
    lookup_field = "id"

    def get_object(self):
        # using the id of the company to filter through the leads
        company_id = self.kwargs.get("company_id")
        # the lead id on the url
        id = self.kwargs.get("id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        # get the lead base on the id of the company on the urls
        lead = company.leadcontact_set.filter(id=id).first()
        if not lead:
            raise Http404
        return lead

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer = LeadContactSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        #  now with the feedback data was
        #  passed also if available when updating the lead we need to create a feedback
        feedback_serializer = FeedbackCreateSerializer(data=request.data)
        #  check if the feedback serializer is valid and if it would not raise an exception
        if feedback_serializer.is_valid(raise_exception=False):
            feedback_content = feedback_serializer.validated_data.get("feedback_content")
            feedback_action = feedback_serializer.validated_data.get("feedback_action")
            feedback_next_schedule = feedback_serializer.validated_data.get("feedback_next_schedule")
            #  create the feedback with the helper function provided
            feedback = Feedback.objects.create_by_model_type(
                model_type="leadcontact",
                other_model_id=instance.id,
                feedback=feedback_content,
                action=feedback_action,
                next_schedule=feedback_next_schedule,
                staff=self.request.user
            )

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)


