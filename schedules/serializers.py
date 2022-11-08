from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyGroupSerializer, CompanySerializer
from companies.utils import check_group_is_under_company
from schedules.models import UserScheduleCall, ScheduleCall


class ScheduleCallSerializer(serializers.ModelSerializer):
    """
    This serializes the schedule call which is either
    """

    class Meta:
        model = ScheduleCall
        fields = [
            "id",
            "title",
            "minutes",
            "meeting_link",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]


class UserScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    This is used to create or update a schedule
    """
    groups = CompanyGroupSerializer(many=True)

    class Meta:
        model = UserScheduleCall
        fields = [
            "id",
            "groups",
            "first_name",
            "last_name",
            "age_range",
            "email",
            "location",
            "gender",
            "phone",
            "age",
            "communication_medium",
            "will_subscribe",
            "scheduled_date",
            "scheduled_time",
            "employed",
            "other_training",
            "other_training_lesson",
            "will_pay",
            "income_range",
            "knowledge_scale",
            "have_laptop",
            "will_get_laptop",
            "when_get_laptop",
            "good_internet",
            "weekly_commitment",
            "saturday_check_in",
            "more_details",
            "kids_count",
            "kids_years",
            "time_close_from_school",
            "user_type",
            "schedule_call",
            "lead_contact",
            "eligible",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]

    def create(self, validated_data):
        # the groups are in this form groups=[<group instance>, ...] which are the instances
        # of a category
        groups = validated_data.pop('groups')
        instance = UserScheduleCall.objects.create(**validated_data)
        for item in groups:
            # check if the user has access
            if not check_group_is_under_company(instance.company, item):
                raise ValidationError("You dont have access to the groups provided")
            try:
                instance.groups.add(item)
            except Exception as a:
                print(a)
        return instance


class UserScheduleSerializer(serializers.ModelSerializer):
    """
    This is used to get the detail of  a schedule
    """
    schedule_call = ScheduleCallSerializer(read_only=True)
    groups = CompanyGroupSerializer(many=True)
    company = CompanySerializer(many=True)

    class Meta:
        model = UserScheduleCall
        fields = [
            "id",
            "company",
            "groups",
            "staff",
            "first_name",
            "last_name",
            "age_range",
            "email",
            "location",
            "gender",
            "phone",
            "age",
            "communication_medium",
            "will_subscribe",
            "scheduled_date",
            "scheduled_time",
            "employed",
            "other_training",
            "other_training_lesson",
            "will_pay",
            "income_range",
            "knowledge_scale",
            "have_laptop",
            "will_get_laptop",
            "when_get_laptop",
            "good_internet",
            "weekly_commitment",
            "saturday_check_in",
            "more_details",
            "kids_count",
            "kids_years",
            "time_close_from_school",
            "user_type",
            "schedule_call",
            "lead_contact",
            "eligible",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]
