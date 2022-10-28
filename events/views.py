from django.http import Http404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from companies.models import Company
from companies.utils import check_marketer_and_admin_access_company
from events.models import Event
from events.serializers import EventSerializer
from users.permissions import NotLoggedInPermission, LoggedInPermission


class EvenListAPIView(ListAPIView):
    serializer_class = EventSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "title"
    ]
    permission_classes = [NotLoggedInPermission]
    queryset = Event.objects.all()

    def get_queryset(self):
        """this is getting the filtered queryset from search filter
                 then adding more filtering   """
        queryset = self.filter_queryset(self.queryset.all())
        # FIXME: ASK QUESTION ON HOW THE QUERY WILL LOOK LIKE

        return queryset


class EventCreateAPIView(CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [LoggedInPermission]
    queryset = Event.objects.all()

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

    def get_queryset(self):
        event_qs = Event.objects.filter(company=self.get_company())
        return event_qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company, staff=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [NotLoggedInPermission]
    lookup_field = "id"

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

    def get_queryset(self):
        #  if the method is GET . that means the user just want to check not posting or updating the event .
        #  so this can enable other user to be able to view the event
        if self.request.method == "GET":
            event = Event.objects.all()
        else:
            event = Event.objects.filter(company=self.get_company())
        return event

    def update(self, request, *args, **kwargs):
        # check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are not authenticated"}, status=400)
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(staff=self.request.user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are not authenticated"}, status=400)
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins or  the assigned marketer
        if not check_marketer_and_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=400)
        self.perform_destroy(instance)
        return Response(status=204)
