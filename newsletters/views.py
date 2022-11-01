from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from companies.models import Company
from companies.utils import check_marketer_and_admin_access_company
from users.permissions import NotLoggedInPermission, LoggedInPermission
from .models import CompanySubscriber
from .serializers import CompanySubscriberSerializer, AddToLeadBoardSerializer
from leads.models import LeadContact


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
        serializer = CompanySubscriberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_id = serializer.validated_data.get("group_id")

        # check if the group_id passed is under that company
        if not self.get_company().group_set.filter(id=group_id).first():
            return Response({"error": "You dont have access to to use this group id for this company "})
        # using the get company i created to set the company
        serializer.save(company=self.get_company())
        return Response(serializer.data, status=201)

    def get_queryset(self):
        """
        return all subscribers

        This only shows those subscribers that are not on leadboard.
        :return:wo
        """
        company = self.get_company()
        # return subscribed email
        subscribed = self.request.query_params.get("subscribed")
        group_id = self.request.query_params.get("group_id")
        queryset = CompanySubscriber.objects.filter(company=company)
        #  if the group id was passed
        if group_id:
            queryset = CompanySubscriber.objects.filter(
                company=company, group_id=group_id
                , on_leadboard=False)
        if subscribed == "true":
            #  if the group id was passed
            if group_id:
                return CompanySubscriber.objects.filter(company=company, subscribed=True,
                                                        group_id=group_id, on_leadboard=False)
            return CompanySubscriber.objects.filter(company=company, subscribed=True, on_leadboard=False)
        if subscribed == "false":
            #  if the group id was passed
            if group_id:
                return CompanySubscriber.objects.filter(company=company, subscribed=True, group_id=group_id,
                                                        on_leadboard=False)
            return CompanySubscriber.objects.filter(company=company, subscribed=True, on_leadboard=False)
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


class AddToLeadBoardAPIView(APIView):
    """
    This enables adding users email to the lead board
    """
    permission_classes = [LoggedInPermission]

    def post(self, request, *args, **kwargs):
        serializer = AddToLeadBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscribers = serializer.validated_data.get("subscribers")
        for item in subscribers:
            company_subscriber = CompanySubscriber.objects.filter(id=item, on_leadboard=False).first()
            if not company_subscriber:
                #  if not the company_subscriber then it re loop
                continue
            #  first check for then company owner then the company admins or  the assigned marketer
            if not check_marketer_and_admin_access_company(self.request.user, company_subscriber.company):
                return Response({"error": "You dont have permission"}, status=400)

            if not company_subscriber.company.marketers.all().order_by('?').first():
                return Response({"error": "No marketer currently on company"}, status=400)

            # fixme : fix the way the lead_source or category is used to create the lead contact
            leadboard = LeadContact.objects.create(
                prefix="",
                company=company_subscriber.company,
                staff=self.request.user,
                last_name=company_subscriber.last_name,
                first_name=company_subscriber.first_name,
                email=company_subscriber.email,
                message=company_subscriber.message,
                mobile="",
                lead_source="",
                assigned_marketer=company_subscriber.company.marketers.all().order_by('?').first(),
                gender="",
                category="INFORMATION",
            )
            company_subscriber.on_leadboard = True
            company_subscriber.save()
        return Response({"message": "Successfully added to leadboard"}, status=200)
