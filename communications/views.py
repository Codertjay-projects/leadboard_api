from django.http import Http404, HttpResponseRedirect
from django.views import View
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.models import SendGroupsEmailScheduler, SendCustomEmailScheduler
from communications.serializers import SendGroupsEmailSchedulerSerializer, SendGroupsEmailSchedulerListSerializer, \
    SendCustomEmailSchedulerSerializer, SendCustomEmailListSchedulerSerializer
from companies.models import Company
from companies.utils import check_admin_access_company
from high_value_contents.models import DownloadHighValueContent
from users.permissions import LoggedInPermission
from .models import SendCustomEmailSchedulerLog, SendGroupsEmailSchedulerLog
from .tasks import create_custom_schedule_log, create_group_schedule_log


class SendGroupsEmailSchedulerListCreateAPIView(ListCreateAPIView):
    """
    this list all mails sent or fail which are sent to groups of users on leads
    """
    permission_classes = [LoggedInPermission]
    serializer_class = SendGroupsEmailSchedulerSerializer
    queryset = SendGroupsEmailScheduler.objects.all()

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
        serializer = self.get_serializer(data=request.data)
        if not check_admin_access_company(user=self.request.user, company=self.get_company()):
            return Response({"error": "You do not have access to this Company"}, status=401)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=self.get_company())
        # Get the instance we just saved using the ID
        instance = SendGroupsEmailScheduler.objects.get(id=serializer.data.get("id"))
        # Create Logs under thus SendCustomEmailScheduler using the task
        create_group_schedule_log.delay(instance.id)
        return Response(serializer.data, status=201)


class SendCustomEmailSchedulerListCreateAPIView(ListCreateAPIView):
    """
    this list all mails sent or fail which are sent to groups of users on leads
    """
    permission_classes = [LoggedInPermission]
    serializer_class = SendCustomEmailSchedulerSerializer
    queryset = SendCustomEmailScheduler.objects.all()

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SendCustomEmailListSchedulerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Filter the query set base on the company provided"""
        queryset = self.filter_queryset(self.queryset.filter(company=self.get_company()))
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not check_admin_access_company(user=self.request.user, company=self.get_company()):
            return Response({"error": "You do not have access to this Company"}, status=401)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=self.get_company())
        # Get the instance we just saved using the ID
        instance = SendCustomEmailScheduler.objects.get(id=serializer.data.get("id"))
        # Create Logs under thus SendCustomEmailScheduler using the task
        create_custom_schedule_log.delay(instance.id)
        return Response(serializer.data, status=201)


class EmailUpdateLinkClickedView(View):
    """
    This update the view counts of email logs  for custom and group emails
    ALso it used to verify the email of the user
    Base on the email_type we set of logic
    if the email_type is custom or group we only need to append the links clicked
    , if it is high_value_content then we set the email to be verified

    """

    def get(self, request, *args, **kwargs):
        email_type = request.GET.get('email_type')
        redirect_url = request.GET.get('redirect_url')
        email_id = request.GET.get('email_id')
        if email_type == "custom":
            log = SendCustomEmailSchedulerLog.objects.filter(id=email_id).first()
            if log:
                log.links_clicked = f"{log.links_clicked},{redirect_url}"
                log.save()
        if email_type == "group":
            # if the email type is group then we add the links to the group
            log = SendGroupsEmailSchedulerLog.objects.filter(id=email_id).first()
            if log:
                log.links_clicked = f"{log.links_clicked},{redirect_url}"
                log.save()
        if email_type == "high_value_content":
            # filter for the high value content
            download_high_value_content = DownloadHighValueContent.objects.filter(
                id=email_id).first()
            # Verify the user email
            if download_high_value_content:
                download_high_value_content.verified = True
                download_high_value_content.is_safe = True
                download_high_value_content.save()

        return HttpResponseRedirect(redirect_url)


class EmailUpdateViewCountAPIView(APIView):
    """
    This view is used to increase the number of read email by the users on the organisation
    using the organisations ID

    This would be set on the mail as an image
    """

    def get(self, request, *args, **kwargs):
        email_type = self.request.GET.get("email_type")
        email_id = self.request.GET.get("email_id")
        if email_type == "group":
            # Update the SendGroupsEmailSchedulerLog  view count if the email type is custom
            log = SendGroupsEmailSchedulerLog.objects.filter(id=email_id).first()
            if log:
                log.view_count += 1
                log.save()
        if email_type == "custom":
            # Update the SendCustomEmailSchedulerLog  view count if the email type is custom
            log = SendCustomEmailSchedulerLog.objects.filter(id=email_id).first()
            if log:
                log.view_count += 1
                log.save()
        return Response({"message": "Successfully open mail"}, status=200)
