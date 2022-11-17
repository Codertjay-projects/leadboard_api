from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserDetailSerializer
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    staff = UserDetailSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Event
        fields = [
            "id",
            "staff",
            "company_id",
            "title",
            "email",
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
        ]
        read_only_fields = [
            "id",
            "company_id",
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
