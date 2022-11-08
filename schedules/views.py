from django.http import Http404
# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from companies.models import Company
from schedules.serializers import UserScheduleSerializer, UserScheduleCreateUpdateSerializer
from users.permissions import LoggedInPermission, NotLoggedInPermission


class UserScheduleCallListCreateAPIView(ListCreateAPIView):
    """
    This is used to list or create a user schedule
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = UserScheduleSerializer

    def get_company(self):
        #  filter the company base on the id provided
        company_id = self.kwargs.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def create(self, request, *args, **kwargs):
        company = self.get_company()
        serializer = UserScheduleCreateUpdateSerializer(
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company)
        return Response(serializer.data, status=201)


class UserScheduleCallRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to get the detail of a user schedule and also delete the user schedule
    """
    permission_classes = [LoggedInPermission]
    serializer_class = UserScheduleSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if check_marketer_and_admin_access_group
        #     self.perform_destroy(instance)
        return Response(status=204)
