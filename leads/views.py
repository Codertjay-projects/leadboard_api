from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
import uuid
import json
from rest_framework.views import APIView

from companies.models import Company, CompanyEmployee, Group
from companies.utils import check_marketer_and_admin_access_company, check_company_high_value_content_access, \
    get_assigned_marketer_from_company_user_schedule_call, get_assigned_marketer_from_company_lead, get_company
from feedbacks.models import Feedback
from feedbacks.serializers import FeedbackCreateSerializer
from users.permissions import LoggedInPermission, NotLoggedInPermission
from users.utils import date_filter_queryset, is_valid_uuid
from users.models import User
from .models import LeadContact
from .serializers import LeadContactUpdateCreateSerializer, LeadContactDetailSerializer
from django.db.models import Q


class LeadContactCreateListAPIView(ListCreateAPIView):
    """
    This class is meant to list all the lead contact and also create a new one
    """
    permission_classes = [LoggedInPermission]
    serializer_class = LeadContactDetailSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "last_name",
        "first_name",
        "middle_name",
        "job_title",
        "email",
    ]

    def filter_queryset(self, queryset):
        """overriding the filter queryset and filter  for multiple values if exists
         for example if the &search=favour afenikhena, if search by splitting it
         """
        search_query = self.request.query_params.get('search')
        if search_query:
            search_words = search_query.split()
            q_objects = Q()
            for word in search_words:
                for field in self.search_fields:
                    q_objects |= Q(**{f"{field}__icontains": word})
            queryset = queryset.filter(q_objects)
        return queryset

    def get_company(self):
        #  filter the company base on the id provided
        company_id = is_valid_uuid(self.request.query_params.get("company_id"))
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        """
        this filter using the company id passed on the urls to get the leads associated with it
        """
        lead_type = self.request.query_params.get("lead_type")
        cat = self.request.query_params.get("cat")
        uuid_params = self.request.query_params.get("user")
        staff = User.objects.filter(id=is_valid_uuid(uuid_params)).first()
        # Check if the category is passed
        # get leads base on the company and the cat

        queryset = self.filter_queryset(LeadContact.objects.filter_by_actions(
            action_type=cat, company=self.get_company()))
        # if the lead_type is passed on the params then we set it on the request
        if lead_type:
            lead_type = lead_type.upper()
            queryset = queryset.filter(lead_type=lead_type)
        if staff:
            # get the leads of that's staff
            queryset = queryset.filter(assigned_marketer=staff)
            # print(queryset)
        elif uuid_params and not staff:
            raise APIException({'message': 'No result found'})

        # Filter the date if it is passed in the params like
        if queryset:
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Check if the user have permission to view the list
        if not check_marketer_and_admin_access_company(self):
            # If it doesn't raise an error that means the user is part of the organisation
            return Response({"error": "You dont have permission"}, status=401)
        # Check if the user is among marketers in the company
        if self.request.user.id in self.get_company().all_marketers_user_ids():
            # Filter to get the leads where the user is the assigned marketer
            queryset = queryset.filter(assigned_marketer=self.request.user)
        # paginate the response
        page = self.paginate_queryset(queryset)
        if page is not None:
            # return a paginated response
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        #  before creating a lead we have to make sure the user is a member of that company
        company = self.get_company()
        serializer = LeadContactUpdateCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Getting the email and checking if an email exists on this leads under the company
        email = serializer.validated_data.get("email")
        lead_contact_email_exists = LeadContact.objects.filter(email=email, company=company).first()
        if lead_contact_email_exists:
            # The lead email must be unique under an organisation
            return Response({"email": "Lead with that email already exists under this organisation"}, status=400)

        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        # Get an assigned marketer for the schedule call
        assigned_marketer = get_assigned_marketer_from_company_lead(company)
        serializer.save(company=company, assigned_marketer=assigned_marketer)
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
        company_id = is_valid_uuid(self.request.query_params.get("company_id"))
        # the lead id on the url
        id = self.kwargs.get("id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        # get the lead base on the id of the company on the urls
        lead = LeadContact.objects.filter(company=company).first()
        if not lead:
            raise Http404
        return lead

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = LeadContactDetailSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
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
            feedback = Feedback.objects.create(
                company=instance.company,
                staff=self.request.user,
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                next_schedule=feedback_next_schedule,
                feedback=feedback_content,
                action=feedback_action,
            )

            """End Feedback create"""
            # Update the lead feedback action count
            company_employee = CompanyEmployee.objects.filter(company=instance.company, user=self.request.user).first()
            if company_employee:
                company_employee.lead_actions_count += 1
                company_employee.save()

        ################################################################

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)


class LeadStatsRetrieveAPIView(RetrieveAPIView):
    queryset = Company.objects.all()
    permission_classes = [LoggedInPermission]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        company = self.get_object()

        now = timezone.now()  # get the current time
        time_24_hours_ago = now - timezone.timedelta(hours=24)  # calculate the time 24 hours ago

        schedules = None
        conversion = None
        recent_action = None

        marketer = CompanyEmployee.objects.filter(company=company, user=self.request.user).first()

        # Check if request user is company owner, ADMIN or MARKETER
        if self.request.user == company.owner or marketer.role == 'ADMIN':
            schedules = Feedback.objects.filter(company=company, next_schedule__gt=now).count()
            conversion = LeadContact.objects.filter(company=company, paying=True).count()
            # filter the objects to include only those created within the last 24 hours
            recent_action = Feedback.objects.filter(company=company, timestamp__gte=time_24_hours_ago).count()
        elif marketer.role == 'MARKETER':
            schedules = Feedback.objects.filter(company=company, next_schedule__gt=now, staff=self.request.user).count()
            conversion = LeadContact.objects.filter(company=company, paying=True,
                                                    assigned_marketer=self.request.user).count()
            recent_action = Feedback.objects.filter(company=company, timestamp__gte=time_24_hours_ago,
                                                    staff=self.request.user).count()

        context = {
            'schedules': schedules,
            'all_leads': LeadContact.objects.filter(company=company).count(),
            'conversion': conversion,
            'recent_action': recent_action,

        }

        return Response(context, status=status.HTTP_200_OK)


class LeadUploadAPIView(APIView):
    """
    this is used to upload lead in json format
    """
    permission_classes = [LoggedInPermission]

    def post(self, request):
        # the data name is called a file
        company = get_company(self)
        data = self.request.data
        
        try:
            for item in data:
                group, group_created = Group.objects.get_or_create(
                    title=item.get("group").upper().replace(" ","_"),
                    company=company)
                # Get or create the lead contact
                lead_contact = LeadContact.objects.filter(email=item.get("email"), company=company).first()
                lead_type = item.get("lead_type", '')
                if lead_type:
                    lead_type = lead_type.upper()
                else:
                    lead_type = None
                print(lead_contact)
                if not lead_contact:
                    lead_contact = LeadContact()
                    lead_contact.email = item.get("email")
                    lead_contact.company = company
                # Update the lead contact with the data provided
                lead_contact.prefix = item.get("prefix", lead_contact.prefix)
                lead_contact.lead_type = lead_type
                lead_contact.last_name = item.get("last_name", lead_contact.last_name)
                lead_contact.first_name = item.get("first_name", lead_contact.first_name)
                lead_contact.middle_name = item.get("middle_name", lead_contact.middle_name)
                lead_contact.job_title = item.get("job_title", lead_contact.job_title)
                lead_contact.sector = item.get("sector", lead_contact.sector)
                lead_contact.mobile = item.get("phone", lead_contact.mobile)
                lead_contact.gender = item.get("gender", lead_contact.gender)
                lead_contact.send_email = item.get("send_email", lead_contact.send_email)
                lead_contact.lead_source = item.get("lead_source", lead_contact.lead_source)
                lead_contact.is_safe = item.get("is_safe", lead_contact.is_safe)

                # filter for the assigned marketer
                marketer_email = item.get("assigned_marketer")
                if marketer_email:
                    assigned_marketer = company.employees.filter(user__email=marketer_email).first()
                    print(assigned_marketer)
                    if not assigned_marketer:
                        assigned_marketer = get_assigned_marketer_from_company_lead(company)
                    # add the assigned marketer
                else:
                    assigned_marketer = get_assigned_marketer_from_company_lead(company)

                lead_contact.assigned_marketer = assigned_marketer
                lead_contact.save()
                lead_contact.groups.add(group)

        except Exception as a:
            print(a)
            return Response({"error": f'{a}'}, status=400)
        return Response({"message": "Successfully upload"}, status=200)
