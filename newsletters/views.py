from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from companies.models import Company
from companies.utils import check_marketer_and_admin_access_company
from users.permissions import NotLoggedInPermission
from .models import CompanySubscriber
from .serializers import CompanySubscriberSerializer


class CompanySubscriberViewSetsAPIView(ModelViewSet):
    serializer_class = CompanySubscriberSerializer
    permission_classes = [NotLoggedInPermission]
    lookup_field = "id"

    def get_company(self, *args, **kwargs):
        # the company id
        company_id = self.request.query_params.get("company_id")
        #  this filter base on the company id  provided
        if not company_id:
            raise Http404
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #  using the get company i created to set the company
        serializer.save(company=self.get_company())
        return Response(serializer.data, status=201)

    def get_queryset(self):
        """
        return all subscribers
        :return:wo
        """
        company = self.get_company()
        # return subscribed email
        subscribed = self.request.query_params.get("subscribed")
        queryset = CompanySubscriber.objects.filter(company=company)
        if subscribed == "true":
            return CompanySubscriber.objects.filter(company=company, subscribed=True)
        if subscribed == "false":
            return CompanySubscriber.objects.filter(company=company, subscribed=True)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
