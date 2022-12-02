from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyInfoSerializer
from users.serializers import UserDetailSerializer
from .models import Event, EventRegister


class EventRegisterSerializer(serializers.ModelSerializer):
    """
    this serializer is used to register for an event
    """

    class Meta:
        model = EventRegister
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "gender",
            "age_range",
            "will_receive_email",
            "accept_terms_and_conditions",
            "timestamp",
        ]


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
            "timestamp"
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
