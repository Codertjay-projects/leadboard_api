from django.http import Http404
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from companies.models import Company, Group
from companies.utils import check_marketer_and_admin_access_company, get_assigned_marketer_from_company_lead
from leads.models import LeadContact
from users.permissions import NotLoggedInPermission, LoggedInPermission
from users.utils import date_filter_queryset
from .models import ContactUs, Newsletter
from .serializers import ContactUsSerializer, AddToLeadBoardSerializer, NewsletterSerializer


class ContactUsViewSetsAPIView(ModelViewSet):
    serializer_class = ContactUsSerializer
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
        serializer = ContactUsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get Or create the group
        group, created = Group.objects.get_or_create(
            title="ContactUs",
            company=self.get_company()
        )
        # using the get company i created to set the company
        serializer.save(company=self.get_company(), group=group)
        return Response(serializer.data, status=201)

    def get_queryset(self):
        """
        return all contactus
        This only shows those contactus that are not on leadboard.
        :return:wo
        """
        company = self.get_company()
        # return contactus not on leadboard
        queryset = self.filter_queryset(ContactUs.objects.filter(company=company, on_leadboard=False))
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, instance.company):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class AddToLeadBoardAPIView(APIView):
    """
    This enables adding users email to the lead board
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = AddToLeadBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contactus_infos = serializer.validated_data.get("contactus_infos")
        for item in contactus_infos:
            contactus = ContactUs.objects.filter(id=item, on_leadboard=False).first()
            company = contactus.company
            if not contactus:
                #  if not the contactus then it re loop
                continue
            lead_contact, created = LeadContact.objects.get_or_create(
                prefix="",
                lead_type="CONTACTUS",
                company=contactus.company,
                last_name=contactus.last_name,
                first_name=contactus.first_name,
                email=contactus.email,
                mobile="",
                lead_source="OTHERS",
                gender="",
                category="INFORMATION",
            )
            lead_contact.message = contactus.message
            lead_contact.assigned_marketer = get_assigned_marketer_from_company_lead(company)
            if contactus.group:
                # if the contactus contains a group then we need to add it to the leadboard
                lead_contact.groups.add(contactus.group)
            lead_contact.save()
            contactus.on_leadboard = True
            contactus.save()
        return Response({"message": "Successfully added to leadboard"}, status=200)


class NewsletterListCreateAPIView(ListCreateAPIView):
    permission_classes = [NotLoggedInPermission]
    serializer_class = NewsletterSerializer
    queryset = Newsletter.objects.all()

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

    def get_queryset(self):
        company = self.get_company()
        queryset = self.filter_queryset(self.queryset.filter(company=company))
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        # Get the company associated
        company = self.get_company()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        # Check if the user has already subscribed to this newsletter
        if Newsletter.objects.filter(company=company, email=email).exists():
            return Response({"error": "Already Subscribed to newsletter"}, status=400)
        serializer.save(company=company)
        return Response(serializer.data, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Check if the user have permission to access this
        if not self.request.user.is_authenticated:
            return Response({"error": "You need to be logged in"}, status=401)
        # Check if the user has permission to view the newsletters
        if not check_marketer_and_admin_access_company(user=self.request.user, company=self.get_company()):
            return Response({"error": "You dont have permission to view the emails"}, status=401)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NewsletterDeleteAPIView(DestroyAPIView):
    permission_classes = [LoggedInPermission]
    lookup_field = "id"
    queryset = Newsletter.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user have permission to access this
        if not self.request.user.is_authenticated:
            return Response({"error": "You need to be logged in"}, status=401)
        # Check if the user has permission to view the newsletters
        if not check_marketer_and_admin_access_company(user=self.request.user, company=instance.company):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)



