from django.http import Http404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.permissions import LoggedInPermission
from .models import Company, Location, Industry, Group
from .serializers import CompanyCreateUpdateSerializer, CompanySerializer, CompanyAddUserSerializer, \
    CompanyGroupSerializer, LocationSerializer, IndustrySerializer, CompanyRequestSerializer, OwnerAddUserSerializer

from .tasks import send_request_to_user, send_request_to_admin


class CompanyListCreateAPIView(ListCreateAPIView):
    """
    This is meant to create the company for a user wo who wish to have one
    """
    permission_classes = [LoggedInPermission]
    serializer_class = CompanyCreateUpdateSerializer

    def get_queryset(self):
        # it filters the company base on the owner
        return Company.objects.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CompanySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompanySerializer(queryset, many=True)
        return Response(serializer.data)


class CompanyRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    """
    This deletes all company's and also groups that are associated with it, or it updates the company
    """
    permission_classes = [LoggedInPermission]
    lookup_field = "id"

    def get_queryset(self):
        return Company.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # check the company owner or admins if the user has access
        if request.user != instance.owner:
            if request.user not in instance.admins.all():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        self.perform_destroy(instance)
        return Response(status=204, data={"message": "Successfully deleted the company"})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CompanySerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # check the company owner or admins if the user has access
        if request.user != instance.owner:
            if request.user not in instance.admins.all():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        serializer = CompanyCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CompanyAddUserAPIView(APIView):
    """
    This class is meant to create marketer in a company or remove from the existing once base on
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = CompanyAddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_user_type = serializer.validated_data.get("company_user_type")
        action = serializer.validated_data.get("action")
        email = serializer.validated_data.get("email")
        #  get the id of the company
        id = kwargs.get("id")
        company = Company.objects.filter(id=id).first()
        if not company:
            return Response(status=404, data={"error": "Company does not exist"})
        # check the company owner or admins if the user has access
        if request.user != company.owner:
            #  check if the user is among the admins in the company
            if request.user not in company.admins.all():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        # check the email if it is a registered one
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(status=400, data={"error": "User does not exist"})
        # check the action
        if action == "ADD" and company_user_type == "ADMIN":
            if user not in company.admins.all():
                company.admins.add(user)
                company.save()
                return Response({"message": "Successfully add user as admin to this company "}, status=200)
            return Response({"error": "User already an admin"}, status=400)
        elif action == "DELETE" and company_user_type == "ADMIN":
            if user in company.admins.all():
                company.admins.remove(user)
                company.save()
                return Response({"message": "Successfully remove user as admin on this company "}, status=200)
            return Response({"error": "User not  an admin"}, status=400)
        elif action == "ADD" and company_user_type == "MARKETER":
            if user not in company.marketers.all():
                company.marketers.add(user)
                company.save()
                return Response({"message": "Successfully add user as marketer to this company "}, status=200)
            return Response({"error": "User already a marketer"}, status=400)
        elif action == "DELETE" and company_user_type == "MARKETER":
            if user in company.marketers.all():
                company.marketers.remove(user)
                company.save()
                return Response({"message": "Successfully remove user as a marketer on this company "}, status=200)
            return Response({"error": "User not a marketer"}, status=400)
        return Response({"error": "Unknown error occurred"}, status=500)


class CompanyGroupListCreate(ListCreateAPIView):
    """
    This is meant to list all the groups which is under a company and also create a new one .
    Note the user creating the group must be and admin in the company or the owner
    """
    permission_classes = [LoggedInPermission]
    serializer_class = CompanyGroupSerializer

    def get_company(self):
        #  the company id passed in the params
        id = self.kwargs.get("id")
        company = Company.objects.filter(id=id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        groups = Group.objects.filter(company_id=self.get_company().id)
        return groups

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = self.get_company()
        # check the company owner or admins if the user has access
        if request.user != company.owner:
            if request.user not in company.admins.all():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        # adding the company to the group
        serializer.save(company=company)
        return Response(serializer.data, status=201)


class CompanyGroupRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    This class is meant to delete the group on a company
    and the user who is performing the request must be the owner or an admin of the company
    """
    permission_classes = [LoggedInPermission]
    serializer_class = CompanyGroupSerializer

    def get_object(self):
        #  get the company id from kwargs and also the group id
        company_id = self.kwargs.get("company_id")
        group_id = self.kwargs.get("group_id")
        #  filter the company and get the groups under that company
        company = Company.objects.filter(id=company_id).first()
        group = company.group_set.filter(id=group_id).first()
        if not group:
            raise Http404
        return group

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # check the company owner or admins if the user has access
        if request.user != instance.company.owner:
            if request.user not in instance.company.admins.all():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # check the company owner or admins if the user has access
        if request.user != instance.company.owner:
            if request.user not in instance.company.admins.all():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        serializer = CompanyGroupSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class LocationViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = LocationSerializer
    permission_classes = [LoggedInPermission]
    queryset = Location.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  i added partial true to prevent required for updating value
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class IndustryViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = IndustrySerializer
    permission_classes = [LoggedInPermission]
    queryset = Industry.objects.all()


class RequestToJoinCompanyAPIView(APIView):
    """
    This is meant to send a request to the owner of the company
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        # The company id is sent by the user so that way a request model is sent.
        serializer = CompanyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_id = serializer.data.get("company_id")
        message = serializer.data.get("message")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            return Response({"error": "Company with this ID does not exists"}, status=400)
        # Instead of creating a model thinking of sending both the company owner and the user a message
        # Send message to both admin and the user sending the request
        send_request_to_user.delay(self.request.user.email, company.name)
        send_request_to_admin.delay(company.owner.email, self.request.user.email, message)
        return Response({"message": "Successfully sent request to Join company"})


class OwnerAddUserToCompany(APIView):
    """
    The class is meant for the owner tob add a user to the company , remove and also choose what role the user is
    play either as an admin or a marketer
    """

    def post(self, request, *args, **kwargs):
        serializer = OwnerAddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_id = serializer.data.get("company_id")
        email = serializer.data.get("email")
        role = serializer.data.get("role")
        action = serializer.data.get("action")
        # Check if a company with the ID exists
        company = Company.objects.filter(id=company_id).first()
        if not company:
            return Response({"error": "Company with this ID does not exists"}, status=400)


        return Response()
