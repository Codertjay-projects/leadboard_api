from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from companies.models import Company
from companies.utils import check_marketer_and_admin_access_company
from high_value_contents.models import HighValueContent
from high_value_contents.serializers import HighValueContentSerializer
from users.permissions import LoggedInPermission


class HighValueContentViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = HighValueContentSerializer
    permission_classes = [LoggedInPermission]

    def get_company(self):
        # the company id
        company_id = self.request.query_params.get("company_id")
        #  this filter base on the lead id  provided
        if not company_id:
            raise Http404
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self, *args, **kwargs):
        #  using the company method e created as an helper function
        company = self.get_company()
        feedback = HighValueContent.objects.filter(company=company)
        return feedback

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)
