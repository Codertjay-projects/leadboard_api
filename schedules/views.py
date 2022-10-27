from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from schedules.serializers import UserScheduleSerializer, UserScheduleCreateUpdateSerializer
from users.permissions import LoggedInPermission


class UserScheduleCallListCreateAPIView(ListCreateAPIView):
    """
    This is used to list or create a user schedule
    """
    permission_classes = [LoggedInPermission]
    serializer_class = UserScheduleSerializer

    def create(self, request, *args, **kwargs):
        #  passing context to the serializer to enable us to access the loggedin user
        # but we use the request to access which user is creating the the user schedule and if he
        # or she has access
        serializer = UserScheduleCreateUpdateSerializer(
            data=request.data,
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


class UserScheduleCallRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to get the detail of a user schedule and also delete the user schedule
    """
    permission_classes = [LoggedInPermission]
    serializer_class = UserScheduleSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if check_marketer_and_admin_access_group
        self.perform_destroy(instance)
        return Response(status=204)