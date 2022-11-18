from django.http import Http404
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from companies.models import Company
from companies.utils import check_marketer_and_admin_access_company, get_assigned_marketer_from_company_lead
from high_value_contents.models import HighValueContent, DownloadHighValueContent
from high_value_contents.serializers import HighValueContentSerializer, DownloadHighValueContentSerializer, \
    DownloadHighValueContentDetailSerializer
from high_value_contents.tasks import send_high_value_content_verify
from users.permissions import LoggedInPermission, NotLoggedInPermission


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
            return Response({"error": "You dont have permission"}, status=401)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)


class DownloadHighValueContentListCreateAPIView(ListCreateAPIView):
    """
    This is used to download the high value content where the user fills out information which is being sent to the lead
    but before that we verify the email first
    """
    serializer_class = DownloadHighValueContentSerializer
    permission_classes = [NotLoggedInPermission]

    def get_high_value_content(self):
        # the high_value_content_id
        high_value_content_id = self.request.query_params.get("high_value_content_id")
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
        company = self.get_high_value_content().company
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(high_value_content=self.get_high_value_content())
        # fixme: send an email to the user containing the detail url once the user view the link we verify the email
        # and also send the info to the lead
        send_high_value_content_verify.delay(
            company_email=company.owner.email,
            first_name=serializer.validated_data.get("first_name"),
            last_name=serializer.validated_data.get("last_name"),
            email=serializer.validated_data.get("email"),
            high_value_content_id=high_value_content.id,
        )
        return Response({"message": "An link of the file has been sent to your email", "data": serializer.data},
                        status=201)


class DownloadHighValueContentRetrieveAPIView(RetrieveAPIView):
    """
    this get the detail info of the high value content and the trying to get it
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = DownloadHighValueContentDetailSerializer
    lookup_field = "id"
    queryset = DownloadHighValueContent.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """
        """
        # Set the email to be verified
        instance = self.get_object()
        instance.verified = True
        instance.is_safe = True

        instance.save()
        ################################################################
        # Lets move the info to the lead board
        # I am importing it here since this is the only place i will use it
        from leads.models import LeadContact
        lead_contact = LeadContact.objects.create(
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
            lead_source=instance.lead_source,
            verified=instance.verified,
            is_safe=instance.is_safe,
            want=instance.want,
            company=instance.high_value_content.company,
            assigned_marketer=get_assigned_marketer_from_company_lead(instance.high_value_content.company)
        )
        # Set the  group
        if instance.high_value_content.group:
            lead_contact.groups.add(instance.high_value_content.group)
            lead_contact.save()
        # set the instance that it has been shown on the leadboard
        instance.on_leadboard = True
        instance.save()
        ################################################################
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
