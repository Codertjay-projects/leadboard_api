from django.http import Http404
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from communications.models import SendEmailScheduler
from communications.serializers import SendGroupsEmailSchedulerSerializer, SendGroupsEmailSchedulerListSerializer, \
    SendCustomEmailSchedulerSerializer, SendCustomEmailListSchedulerSerializer
from companies.models import Company
from companies.utils import check_admin_access_company, get_or_create_test_group
from users.permissions import LoggedInPermission
from .tasks import create_custom_schedule_log, create_group_schedule_log


class SendGroupsEmailSchedulerListCreateAPIView(ListCreateAPIView):
    """
    this list all mails sent or fail which are sent to groups of users on leads
    """
    permission_classes = [LoggedInPermission]
    serializer_class = SendGroupsEmailSchedulerSerializer
    queryset = SendEmailScheduler.objects.all()

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        """Filter the query set base on the company provided"""
        queryset = self.filter_queryset(self.queryset.filter(company=self.get_company()))
        return queryset

    def list(self, request, *args, **kwargs):
        """Overriding the list method to list all the mails .
         I only did this just to change the email I am currently sending """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SendGroupsEmailSchedulerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # this is used if it's a test mail
        is_test = request.data.get("test")
        if is_test:
            is_test = is_test.capitalize()
        serializer = self.get_serializer(data=request.data)
        if not check_admin_access_company(self):
            return Response({"error": "You do not have access to this Company"}, status=401)
        serializer.is_valid(raise_exception=True)
        test_group = get_or_create_test_group(self.get_company())
        # it's on string format
        if is_test == "True":
            # add the test groups and also make the schedule date now
            instance = serializer.save(company=self.get_company(), scheduled_date=timezone.now())
            instance.groups.clear()
            instance.groups.add(test_group)
        else:
            instance = serializer.save(company=self.get_company())
        # Create Logs under thus SendCustomEmailScheduler using the task
        create_group_schedule_log.delay(instance.id)
        return Response(serializer.data, status=201)


class SendCustomEmailSchedulerListCreateAPIView(ListCreateAPIView):
    """
    this list all mails sent or fail which are sent to groups of users on leads
    """
    permission_classes = [LoggedInPermission]
    serializer_class = SendCustomEmailSchedulerSerializer

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        # this is used to get all custom mails sent by
        queryset = self.filter_queryset(
            SendEmailScheduler.objects.filter(
                message_type="CUSTOM", company=self.get_company())
        )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SendCustomEmailListSchedulerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not check_admin_access_company(self):
            return Response({"error": "You do not have access to this Company"}, status=401)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=self.get_company(), message_type="CUSTOM")
        # Get the instance we just saved using the ID
        instance = SendEmailScheduler.objects.get(id=serializer.data.get("id"))
        instance.message_type = "CUSTOM"
        instance.save()
        # Create Logs under thus SendCustomEmailScheduler using the task
        create_custom_schedule_log.delay(instance.id)
        return Response(serializer.data, status=201)
