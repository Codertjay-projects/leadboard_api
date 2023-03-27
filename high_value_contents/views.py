from decouple import config
from django.http import Http404
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from companies.models import Company, Group
from companies.utils import check_marketer_and_admin_access_company, get_assigned_marketer_from_company_lead
from email_logs.tasks import send_custom_mail
from high_value_contents.models import HighValueContent
from high_value_contents.serializers import HighValueContentSerializer, DownloadHighValueContentSerializer, \
    DownloadHighValueContentDetailSerializer
from leads.models import LeadContact
from users.permissions import LoggedInPermission, NotLoggedInPermission
from users.utils import date_filter_queryset, is_valid_uuid


class HighValueContentViewSetsAPIView(ModelViewSet):
    """this viewset enables the full crud which are create, retrieve,update and delete  """
    serializer_class = HighValueContentSerializer
    permission_classes = [LoggedInPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "title",
        "slug",
        "description",
    ]

    def get_company(self):
        # the company id
        company_id = is_valid_uuid(self.request.query_params.get("company_id"))
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
        # Filter through the query set
        queryset = self.filter_queryset(queryset=HighValueContent.objects.filter(company=company))
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        # Get or create the group if it doesn't exist
        group, created = Group.objects.get_or_create(
            title="HIGHVALUECONTENT",
            company=self.get_company()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company, group=group, created_by=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(last_edit_by=self.request.user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response({"message": 'Deleted'}, status=204)


class DownloadHighValueContentListCreateAPIView(ListCreateAPIView):
    """
    This is used to download the high value content where the user fills out information which is being sent to the lead
    but before that we verify the email first
    """
    serializer_class = DownloadHighValueContentSerializer
    permission_classes = [NotLoggedInPermission]

    def get_high_value_content(self):
        # the high_value_content_id
        high_value_content_id = is_valid_uuid(self.request.query_params.get("high_value_content_id"))

        #  this filter base on the high_value_content_id  provided
        if not high_value_content_id:
            raise Http404
        high_value_content = HighValueContent.objects.filter(id=high_value_content_id).first()
        if not high_value_content:
            raise Http404

        return high_value_content

    def create(self, request, *args, **kwargs):
        """
        This first save the info in the DownloadHighValueContent first but after that once we verify the
        user email we save the user info on the lead
        """
        high_value_content = self.get_high_value_content()
        company = high_value_content.company

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead_contact = LeadContact.objects.filter(company=company, email=serializer.validated_data.get("email")).first()
        if not lead_contact:
            lead_contact = LeadContact.objects.create(
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                email=serializer.validated_data.get("email"),
                lead_source=serializer.validated_data.get("lead_source"),
                want=serializer.validated_data.get("want"),
                company=company,
                assigned_marketer=get_assigned_marketer_from_company_lead(company)
            )
        # Set the  group
        if high_value_content.group:
            lead_contact.groups.add(high_value_content.group)
            lead_contact.save()
        # add the user to one of the once that download a lead contact
        high_value_content.lead_contacts.add(lead_contact)

        # This save the email and also through this we know if the mail fail or was su
        send_custom_mail(
            reply_to=high_value_content.company.reply_to_email,
            description=f"""
            You made a request request to download {high_value_content.title} Click the link to download <a 
            href="{config("DOMAIN_NAME")}/api/v1/communications/update_links_clicked/?email_id=
            {serializer.data.get("id")}&email_type=high_value_content&redirect_url={high_value_content.link}"> 
            {high_value_content.title} or click to download file {high_value_content.file}</a>
            """,
            email_subject=f"Download {high_value_content.title}",
            company_name=f"Download {high_value_content.title}",
            email_to=serializer.validated_data.get("email"), )
        return Response({"message": "An link of the file has been sent to your email", "data": serializer.data},
                        status=201)


class LeadsDownloadedHighValueContentRetrieveAPIView(ListAPIView):
    """
    this get all the leads that downloads the high value content
    """
    permission_classes = [LoggedInPermission]
    serializer_class = DownloadHighValueContentDetailSerializer

    def get_queryset(self):
        """
        this returns all individuals downloading high value content
        :return:
        """
        high_value_content_id = is_valid_uuid(self.request.query_params.get("high_value_content_id"))
        if not high_value_content_id:
            raise APIException({"error": "Please provide the high_value_content_id on your params"})
        high_value_content = HighValueContent.objects.filter(id=high_value_content_id).first()
        if not high_value_content:
            raise APIException({"error": "The high_value_content_id is not a valid one"})

        return self.filter_queryset(high_value_content.lead_contacts.all())


class DownloadHighValueDetailsAPIView(RetrieveAPIView):
    """
    Details of downloads
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = HighValueContentSerializer
    lookup_field = "id"
    queryset = HighValueContent.objects.all()

    def get(self, request, *args, **kwargs):
        """
        """
        # Set the email to be verified
        instance = self.get_object()
        print(instance)
        # data = self.custom_retrieve(instance)
        serializer = self.get_serializer(instance)

        return Response(serializer.data)
