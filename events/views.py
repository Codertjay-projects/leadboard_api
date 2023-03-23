from django.http import Http404
from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response

from companies.models import Company
from companies.utils import check_admin_access_company
from email_logs.tasks import send_custom_mail
from events.models import Event, EventRegister
from events.serializers import EventSerializer, EventRegisterSerializer, EventDetailSerializer
from users.permissions import NotLoggedInPermission, LoggedInPermission
from users.utils import date_filter_queryset, is_valid_uuid


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
        # Base on PENDING,PAST and default returns all
        cat = self.request.query_params.get("cat")
        if cat: cat = cat.upper()

        if cat == "UPCOMING":
            # Which means the event has not yet started
            queryset = self.filter_queryset(self.queryset.filter(start_date__gte=timezone.now()))
        elif cat == "COMPLETED":
            # Which means the event has started and have being completed
            queryset = self.filter_queryset(self.queryset.filter(start_date__lt=timezone.now()))
            print(queryset)

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
        company_id = is_valid_uuid(self.request.query_params.get("company_id"))
        #  this filter base on the lead id  provided
        if not company_id:
            raise Http404("Company ID does not exist.")
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise Http404("Company does not exist.")
        return company

    def get_queryset(self):
        event_qs = Event.objects.filter(company=self.get_company())
        return event_qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company = self.get_company()
        #  first check for then company owner then the company admins
        if not check_admin_access_company(self):
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
        company_id = is_valid_uuid(self.request.query_params.get("company_id"))
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
        #  first check for then company owner then the company admins
        if not check_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(staff=self.request.user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # check if the user is authenticated
        if not self.request.user.is_authenticated:
            return Response({"error": "You are not authenticated"}, status=401)

        event_id = is_valid_uuid(kwargs['slug'])
        instance = None

        try:
            instance = Event.objects.get(id=event_id, company=self.get_company())
        except Event.DoesNotExist:
            # Raise Http404 with a 204 status code and a custom message
            raise Http404("Object not found with the given pk") from None

        instance = Event.objects.filter(id=event_id, company=self.get_company()).first()

        #  first check for then company owner then the company admins
        if not check_admin_access_company(self):
            return Response({"error": "You dont have permission"}, status=401)

        self.perform_destroy(instance)
        return Response({"message": "Item deleted."}, status=204)


class EventRegisterAPIView(ListCreateAPIView):
    """
    This is used to register for an event for a normal not logged-in user
    """
    permission_classes = [NotLoggedInPermission]
    serializer_class = EventRegisterSerializer

    def get_event(self):
        """
        this is used to get the event with the event id passed on the params
        """
        event_id = is_valid_uuid(self.request.query_params.get("event_id"))
        #  this filter base on the event id  provided
        if not event_id:
            raise Http404
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise Http404
        return event

    def create(self, request, *args, **kwargs):
        # Get the event
        print('self.get_event()')
        event = self.get_event()
        if event.start_date <= timezone.now():
            return Response({"error": "Event registration closed "}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # i need the company for easy filtering in the communication model for all emails
        serializer.save(event=event, company=event.company)
        # Send in the email to the user registering for the event
        first_name = serializer.validated_data.get("first_name")
        email = serializer.validated_data.get("last_name")
        last_name = serializer.validated_data.get("last_name")

        # Send  mail
        # Send accepted mail
        send_custom_mail(
            company_name=event.company.name,
            description=f"""
            <h2>Hi {first_name} - {last_name},</h2>"
             <p>You have successfully registered for an event </p>
             <p>The event date {event.start_date} and the end time is {event.end_date}.
             The location of the event is {event.location}
            """,
            email_to=email,
            reply_to=event.company.reply_to_email,
            email_subject=f"Registered for Event",

        )
        return Response(
            {"message": "Successfully registered for an event and email has been sent about the event",
             "data": serializer.data}, status=201)


class EventRegisteredUserListAPIView(ListAPIView):
    """
    this is used to get list of people registered under an event
    """
    serializer_class = EventRegisterSerializer
    permission_classes = [LoggedInPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "email",
        "first_name",
        "last_name",
        "mobile",
    ]

    def get_event(self):
        """
        this is used to get an event using the slug passed on the ur
        :return:
        """
        event_slug = self.request.query_params.get("event_slug")
        if not event_slug:
            raise Http404("Event slug not passed")
        event = Event.objects.filter(slug=event_slug).first()
        if not event:
            raise Http404("Event does not exist")
        return event

    def get_queryset(self):
        """
        this is ued to override the queryset and returns the event registered users under an event
        :return:
        """
        queryset = EventRegister.objects.filter(event=self.get_event())
        if queryset:
            # Filter the date if it is passed in the params like
            # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
            # You will get more from the documentation
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        this is used to list all the event registers and i override the default list
        """
        queryset = self.filter_queryset(self.get_queryset())
        event = self.get_event()
        #  first check for then company owner then the company admins
        if event.company.employees.filter(user=self.request.user,
                                          status="ACTIVE", role="ADMIN").first():
            return Response({"error": "You dont have permission"}, status=401)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
