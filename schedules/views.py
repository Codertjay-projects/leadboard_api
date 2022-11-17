from django.http import Http404
# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from companies.models import Company
from companies.utils import get_assigned_marketer_from_company_user_schedule_call, \
    check_marketer_and_admin_access_company, check_admin_access_company
from feedbacks.models import Feedback
from feedbacks.serializers import FeedbackCreateSerializer
from leads.models import LeadContact
from schedules.models import ScheduleCall, UserScheduleCall
from schedules.serializers import UserScheduleSerializer, UserScheduleCreateUpdateSerializer
from users.permissions import LoggedInPermission, NotLoggedInPermission


class UserScheduleCallListCreateAPIView(ListCreateAPIView):
    """
    This is used to list or create a user schedule
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = UserScheduleSerializer
    queryset = UserScheduleCall.objects.all()

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        queryset = self.filter_queryset(self.queryset)
        schedules = queryset.filter(company=self.get_company())
        # Fixme: Fix the search
        return schedules

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Check if the user is logged in
        if not self.request.user.is_authenticated:
            return Response({"error": "Not logged in"}, status=401)
        # Check if the user has permission to view this schedule call
        if not check_marketer_and_admin_access_company(
                company=self.get_company(),
                user=self.request.user):
            return Response(
                {"error": "You dont have permission to view all schedule calls from this company "},
                status=401)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_schedule_call(self):
        """
        Using the schedule call slug which was passed in the urls to get the schedule call
        :return:
        """
        schedule_call_slug = self.request.query_params.get("schedule_call_slug")
        schedule_call = ScheduleCall.objects.filter(slug=schedule_call_slug).first()
        if not schedule_call:
            raise Http404
        return schedule_call

    def create(self, request, *args, **kwargs):
        company = self.get_company()
        schedule_call = self.get_schedule_call()
        serializer = UserScheduleCreateUpdateSerializer(
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        # Check if a customer with the email is already on the leads
        email = serializer.validated_data.get("email")
        lead_contact = LeadContact.objects.filter(email=email).first()
        if not lead_contact:
            lead_contact = None
        # Get an assigned marketer for the schedule call
        assigned_marketer = get_assigned_marketer_from_company_user_schedule_call(company)
        serializer.save(
            company=company,
            schedule_call=schedule_call,
            lead_contact=lead_contact,
            assigned_marketer=assigned_marketer)
        return Response(serializer.data, status=201)


class UserScheduleCallRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to get the detail of a user schedule and also delete the user schedule
    """
    permission_classes = [LoggedInPermission]
    serializer_class = UserScheduleSerializer
    lookup_field = "id"

    def get_queryset(self):
        return UserScheduleCall.objects.filter(company=self.get_company())

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Get the company
        company = self.get_company()
        # Check if the user is the assigned marker
        if not self.request.user == instance.assigned_marketer:
            if not check_admin_access_company(company=company,
                                              user=self.request.user):
                return Response({"error": "You don not have access to update the schedule ."
                                          " Please ask your admin to provide you access"}, status=401)

        serializer = UserScheduleCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ################################################################
        """                 Feedback create                 """
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
                model_type="userschedulecall",
                other_model_id=instance.id,
                feedback=feedback_content,
                action=feedback_action,
                next_schedule=feedback_next_schedule,
                staff=self.request.user
            )
        """End Feedback create"""
        ################################################################

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Get the company
        company = self.get_company()
        # Check if the user is the assigned marker
        if not self.request.user == instance.assigned_marketer:
            if not check_admin_access_company(company=company,
                                              user=self.request.user):
                return Response({"error": "You don not have access to update the schedule ."
                                          " Please ask your admin to provide you access"}, status=401)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if check_marketer_and_admin_access_group
        #     self.perform_destroy(instance)
        return Response(status=204)
