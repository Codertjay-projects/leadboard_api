from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
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
from users.permissions import LoggedInPermission
from users.utils import date_filter_queryset


class UserScheduleCallListCreateAPIView(ListCreateAPIView):
    """
    This is used to list or create a user schedule
    """
    permission_classes = [LoggedInPermission]
    serializer_class = UserScheduleSerializer
    queryset = UserScheduleCall.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "first_name",
        "last_name",
        "assigned_marketer__first_name",
        "assigned_marketer__last_name",
        "age_range",
        "location",
        "gender",
        "communication_medium",
        "catch_up_per_hours_weeks",
        "time_close_from_school",
    ]

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        # Filter the queryset and the backend filter also
        queryset = self.filter_queryset(self.queryset.filter(company=self.get_company()))
        schedule_category = self.request.query_params.get("cat")
        if schedule_category:
            # if past was passed in the params the just filter for the past schedule_category
            if schedule_category.title() == "Past":
                queryset = queryset.filter(scheduled_date__lte=timezone.now())
            else:
                queryset = queryset.filter(schedule_category=schedule_category)
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Check if the user is logged in
        # Check if the user have permission to view the list
        if not check_marketer_and_admin_access_company(self.request.user, self.get_company()):
            # If it doesn't raise an error that means the user is part of the organisation
            return Response({"error": "You dont have permission"}, status=401)
        # Check if the user is among marketers in the company
        if self.request.user.id in self.get_company().all_marketers_user_ids():
            # Filter to get the leads where the user is the assigned marketer
            queryset = queryset.filter(assigned_marketer=self.request.user)

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
        if self.request.user != instance.assigned_marketer:
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
        if self.request.user != instance.assigned_marketer:
            if not check_admin_access_company(company=company,
                                              user=self.request.user):
                return Response({"error": "You don not have access to update the schedule ."
                                          " Please ask your admin to provide you access"}, status=401)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assigned_marketer != self.request.user:
            # if the user is not the assigned marketer
            if not check_admin_access_company(user=self.request.user, company=self.get_company()):
                return Response({"error": "You dont have permission to perform this action"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)
