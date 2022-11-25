from django.http import Http404
from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from companies.models import Company
from companies.utils import check_admin_access_company
from events.models import Event
from events.serializers import EventSerializer, EventRegisterSerializer, EventDetailSerializer
from users.permissions import NotLoggedInPermission, LoggedInPermission
from users.utils import date_filter_queryset
from .tasks import send_user_register_event


class EvenListAPIView(ListAPIView):
    serializer_class = EventSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "title",
        "slug",
        "description",
        "tags",
    ]
    permission_classes = [NotLoggedInPermission]
    queryset = Event.objects.all()

    def get_queryset(self):
        """this is getting the filtered queryset from search filter
                 then adding more filtering   """
        queryset = self.filter_queryset(self.queryset.all())
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
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
        #  first check for then company owner then the company admins
        if not check_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=401)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company, staff=self.request.user)
        return Response(serializer.data, status=201)


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [NotLoggedInPermission]
    lookup_field = "slug"

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EventDetailSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are not authenticated"}, status=401)
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins
        if not check_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(staff=self.request.user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are not authenticated"}, status=401)
        instance = self.get_object()
        company = self.get_company()
        #  first check for then company owner then the company admins
        if not check_admin_access_company(self.request.user, company):
            return Response({"error": "You dont have permission"}, status=401)
        self.perform_destroy(instance)
        return Response(status=204)


class EventRegisterAPIView(CreateAPIView):
    """
    This is used to register for an event for a normal not logged-in user
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = EventRegisterSerializer

    def get_event(self):
        """
        this is used to get the event with the event id passed on the params
        """
        event_id = self.request.query_params.get("event_id")
        #  this filter base on the event id  provided
        if not event_id:
            raise Http404
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise Http404
        return event

    def create(self, request, *args, **kwargs):
        # Get the event
        event = self.get_event()
        if event.start_date <= timezone.now():
            return Response({"error": "Event registration closed "}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        # Send in the email to the user registering for the event
        # we cant pass in the event instance that's why I pass the id instead
        send_user_register_event.delay(
            first_name=serializer.validated_data.get("first_name"),
            last_name=serializer.validated_data.get("last_name"),
            email=serializer.validated_data.get("email"),
            event_id=event.id,
        )
        return Response(
            {"message": "Successfully registered for an event and email has been sent about the event",
             "data": serializer.data}, status=201)