from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserDetailSerializer
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    staff = UserDetailSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "staff",
            "company_id",
            "title",
            "description",
            "image",
            "start_date",
            "end_date",
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
        return attrs
