from django.http import Http404
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.models import SendGroupsEmailScheduler, SendCustomEmailScheduler
from communications.serializers import SendGroupsEmailSchedulerSerializer, SendGroupsEmailSchedulerListSerializer, \
    SendCustomEmailSchedulerSerializer, SendCustomEmailListSchedulerSerializer
from companies.models import Company
from companies.utils import check_admin_access_company
from users.permissions import LoggedInPermission


class EmailReadAPIView(APIView):
    """
    This view is used to increase the number of read email by the users on the organisation
    using the organisations ID

    This would be set on the mail as an image
    """

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get(self, request, *args, **kwargs):
        company = self.get_company()
        return Response({"message": "Successfully open mail"}, status=200)


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
        # Calling the task to schedule the mail we need to send

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
        return Response(serializer.data, status=201)
