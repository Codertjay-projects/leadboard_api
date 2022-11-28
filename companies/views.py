from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.permissions import LoggedInPermission, NotLoggedInPermission
from users.utils import date_filter_queryset
from .models import Company, Location, Industry, Group, CompanyInvite, CompanyEmployee
from .serializers import CompanyCreateUpdateSerializer, CompanySerializer, CompanyInfoSerializer, \
    CompanyModifyUserSerializer, \
    CompanyGroupSerializer, LocationSerializer, IndustrySerializer, CompanyInviteSerializer, \
    CompanyEmployeeSerializer
from .tasks import send_request_to_user
from .utils import check_admin_access_company


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
            if request.user.id not in instance.all_admins_user_ids():
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
            if request.user.id not in instance.all_admins_user_ids():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        serializer = CompanyCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CompanyModifyEmployeeAPIView(APIView):
    """
    This class is meant to create marketer in a company or remove from the existing once base on
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = CompanyModifyUserSerializer(data=request.data)
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
            if request.user.id not in company.all_admins_user_ids():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        # check the email if it is a registered one
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(status=400, data={"error": "User does not exist"})
        # check the action
        if action == "ACTIVATE" and company_user_type == "ADMIN":
            if user.id not in company.all_admins_user_ids():
                # create the admin role
                CompanyEmployee.objects.create_or_update(
                    user=user, company=company, role="ADMIN", status="ACTIVE")
                return Response({"message": "Successfully add user as admin to this company "}, status=200)
            return Response({"error": "User already an admin"}, status=400)
        elif action == "DEACTIVATE" and company_user_type == "ADMIN":
            #  check if the user id's exist in the company employee
            if user.id in company.all_admins_user_ids():
                CompanyEmployee.objects.create_or_update(
                    user=user, company=company, role="ADMIN", status="DEACTIVATE")
                return Response({"message": "Successfully remove user as admin on this company "}, status=200)
            return Response({"error": "User not  an admin"}, status=400)
        elif action == "ACTIVATE" and company_user_type == "MARKETER":
            # activate the user if he or she is an inactive marketer
            if user.id not in company.all_marketers_user_ids():
                CompanyEmployee.objects.create_or_update(
                    user=user, company=company, role="ADMIN", status="ACTIVE")
                return Response({"message": "Successfully add user as marketer to this company "}, status=200)
            return Response({"error": "User already a marketer"}, status=400)
        elif action == "DEACTIVATE" and company_user_type == "MARKETER":
            # deactivate the user if he or she is an active marketer
            if user in company.all_marketers_user_ids():
                CompanyEmployee.objects.create_or_update(
                    user=user, company=company, role="MARKETER",
                    status="DEACTIVATE")
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
        id = self.request.query_params.get("company_id")
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
            if request.user.id not in company.all_admins_user_ids():
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
        company_id = self.request.query_params.get("company_id")
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
            if request.user.id not in instance.company.all_admins_user_ids():
                return Response(status=400, data={"message": "You are not the owner of the company"})
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # check the company owner or admins if the user has access
        if request.user != instance.company.owner:
            if request.user.id not in instance.company.all_admins_user_ids():
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


class CompanyInviteListCreateAPIView(ListCreateAPIView):
    """
    This is meant to list, create the CompanyInvite
    """
    serializer_class = CompanyInviteSerializer
    permission_classes = [LoggedInPermission]

    def get_queryset(self):
        return CompanyInvite.objects.filter(company=self.get_company())

    def get_company(self):
        #  get the company id from kwargs and also the group id
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        company = self.get_company()
        # Check if the user have permission as an admin or owner
        if not check_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission to view invites"}, status=401)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # check the permission
        company = self.get_company()
        if not check_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission to view invites"}, status=401)
        serializer = CompanyInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Check if the mail has been used by the company before and also get the info
        email = serializer.validated_data.get("email")
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        if email:
            if CompanyInvite.objects.filter(email=email, company=self.get_company()).first():
                return Response({"error": "User has already been sent an invitation"}, status=400)
        serializer.save(company=self.get_company())
        # Get the invitation created
        company_invite = CompanyInvite.objects.filter(company=self.get_company(),
                                                      email=serializer.validated_data.get("email")).first()
        if not company_invite:
            return Response(
                {"error": "Error creating invite. If the error continues please contact our customer support"},
                status=500)
        send_request_to_user.delay(
            company_name=company.name,
            invitation_id=company_invite.invite_id,
            first_name=first_name,
            last_name=last_name,
            user_email=email
        )
        return Response(serializer.data, status=201)


class CompanyEmployeesListAPIView(ListAPIView):
    """
    This returns all the marketers available in the company providing the company id
    """
    permission_classes = [LoggedInPermission]
    serializer_class = CompanyEmployeeSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "status",
    ]

    def get_company(self):
        #  get the company id from kwargs and also the group id
        company_id = self.request.query_params.get("company_id")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404
        return company

    def get_queryset(self):
        company = self.get_company()
        company_employees = company.company_employees()
        queryset = self.filter_queryset(company_employees)
        # Filter the date if it is passed in the params like
        # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
        # You will get more from the documentation
        queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset


class InvitedEmployeeSearchCompanyAPIView(ListAPIView):
    permission_classes = [NotLoggedInPermission]
    serializer_class = CompanyInfoSerializer

    def get_queryset(self):
        # Get the email that was sent an invitation
        email = self.request.query_params.get("email")
        if not email:
            raise Http404
        # It could be more than one organisation that sends an invitation to I just need to add the value list
        company_ids_info = CompanyInvite.objects.filter(email=email).values_list("company__id")
        company_list = []
        for item in company_ids_info:
            # Check if the id is not none
            if not item[0]:
                continue
            # Get the company with the ID provided
            company = Company.objects.filter(id=item[0]).first()
            if company:
                company_list.append(company)
        return company_list
