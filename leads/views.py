from django.shortcuts import render
from rest_framework.response import Response

from .models import LeadContact
from users.permissions import LoggedInPermission
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import LeadUpdateCreateSerializer, LeadContactListSerializer


class LeadContactCreateListAPIView(ListCreateAPIView):
    """
    This class is meant to list all the lead contact and also create a new one
    """
    permission_classes = [LoggedInPermission]
    serializer_class = LeadContactListSerializer

    def create(self, request, *args, **kwargs):
        # fixme: verify the user groups
        serializer = LeadUpdateCreateSerializer(data=request.data,context={"request":request})
        serializer.is_valid(raise_exception=True)

        serializer.save(staff=self.request.user)
        return Response(serializer.data, status=201)


class LeadBoardRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    this is used to update the lead , delete i, and also retrieve the lead .
    Note that once the lead is deleted the feedback connected ti will be deleted
    """
    permission_classes = [LoggedInPermission]
    serializer_class = LeadUpdateCreateSerializer
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if instance.group.company.owner != self.request.user or \
                self.request.user not in instance.group.admins.all() or \
                instance.assingned_marketer != self.request.user:
            return Response({"error": "You dont have permission"}, status=400)
        serializer = LeadContactListSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if instance.group.company.owner != self.request.user or \
                self.request.user not in instance.group.admins.all() or \
                instance.assingned_marketer != self.request.user:
            return Response({"error": "You dont have permission"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if instance.group.company.owner != self.request.user or \
                self.request.user not in instance.group.admins.all() or \
                instance.assingned_marketer != self.request.user:
            return Response({"error": "You dont have permission"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)
