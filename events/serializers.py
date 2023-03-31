from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyInfoSerializer
from users.serializers import UserDetailSerializer
from .models import Event, EventRegister

class EventBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "company"
        ]


class EventRegisterSerializer(serializers.ModelSerializer):
    """
    this serializer is used to register for an event
    """
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=250, required=False)
    last_name = serializers.CharField(max_length=250, required=False)
    mobile = serializers.CharField(max_length=250, required=False)
    event = EventBasicSerializer()

    class Meta:
        model = EventRegister
        fields = [
            "id",
            "first_name",
            "last_name",
            "company",
            "email",
            "mobile",
            "gender",
            "age_range",
            "will_receive_email",
            "accept_terms_and_conditions",
            "timestamp",
            "event",
        ]
        read_only_fields =["event"]

    def validate(self, attrs):
        # check if the user is authenticated
        if not self.context["request"].user.is_authenticated:
            if not attrs.get("email"):
                raise serializers.ValidationError("Email required")
            if not attrs.get("first_name"):
                raise serializers.ValidationError("first_name required")
            if not attrs.get("last_name"):
                raise serializers.ValidationError("last_name required")
            if not attrs.get("mobile"):
                raise serializers.ValidationError("mobile required")
            return attrs

        return attrs


class EventSerializer(serializers.ModelSerializer):
    staff = UserDetailSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    company = CompanyInfoSerializer(read_only=True)
    event_register_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "staff",
            "company",
            "title",
            "email",
            "slug",
            "description",
            "image",
            "start_date",
            "end_date",
            "price",
            "link_1",
            "link_2",
            "location",
            "price",
            "tags",
            "is_paid",
            "event_register_count",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "company",
            "timestamp",
            "slug",
        ]

    def validate_start_date(self, start_date):
        #  when updating the start date could be none so i have to prepare for it
        if start_date:
            if start_date < timezone.now():
                raise ValidationError("An error occurred . please the date must be greater than current time ")
        return start_date

    def validate(self, attrs):
        end_date = attrs.get("end_date")
        start_date = attrs.get("start_date")
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("The end date must be correct")
        if attrs.get("is_paid"):
            # Check if is_paid event and if the price was not provided raise an error
            if not attrs.get("price"):
                raise serializers.ValidationError("Price is required for event.")
        return attrs

    def get_event_register_count(self, obj: Event):
        return obj.event_registers().count()


class EventDetailSerializer(serializers.ModelSerializer):
    staff = UserDetailSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    event_registers = serializers.SerializerMethodField(read_only=True)
    company = CompanyInfoSerializer(read_only=True)
    event_register_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "staff",
            "company",
            "title",
            "email",
            "slug",
            "description",
            "image",
            "start_date",
            "end_date",
            "price",
            "link_1",
            "link_2",
            "location",
            "price",
            "tags",
            "is_paid",
            "timestamp",
            "event_register_count",
            "event_registers",

        ]
        read_only_fields = [
            "id",
            "company_id",
            "timestamp"
        ]

    def get_event_registers(self, obj: Event):
        """
        This returns list of the individuals registered for the event
        """
        serializer = EventRegisterSerializer(obj.event_registers(), many=True)
        return serializer.data

    def get_event_register_count(self, obj: Event):
        """returns the number of people registered for the event"""
        return obj.event_registers().count()


class EventSendEmailSerializer(serializers.Serializer):
    """
    this is used to send email to all users registered on all event in a company, each users in just an event
    """
    to_all = serializers.BooleanField(default=False)
    #  the slug field if passed for the event
    event_slug = serializers.SlugField(required=False)
    subject = serializers.CharField(max_length=250)
    message = serializers.CharField(max_length=250)
    schedule_date = serializers.DateTimeField()

    def validate(self, attrs):
        """
        this is used to validate an event
        :return:
        """
        if not attrs.get("event_slug"):
            if not attrs.get("to_all"):
                return serializers.ValidationError("You need to set the event slug or send the message to all event "
                                                   "created by you .")
        return attrs

    def validate_scheduled_date(self, attrs):
        """this is used to validate the schedule date"""
        scheduled_date = attrs
        if scheduled_date < timezone.now():
            raise serializers.ValidationError("The schedule date must be greater than the current date")
        return scheduled_date


