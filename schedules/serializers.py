from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyGroupSerializer
from companies.utils import check_marketer_and_admin_access_group, check_group_is_under_company
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
            "staff",
            "first_name",
            "last_name",
            "phone",
            "gender",
            "age",
            "schedule_date",
            "schedule_time",
            "location",
            "have_laptop",
            "good_internet",
            "weekly_commitment",
            "saturday_check_in",
            "user_type",
            "schedule_call",
            "will_subscribe",
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

    class Meta:
        model = UserScheduleCall
        fields = [
            "id",
            "groups",
            "staff",
            "first_name",
            "last_name",
            "phone",
            "gender",
            "age",
            "schedule_date",
            "schedule_time",
            "location",
            "have_laptop",
            "good_internet",
            "weekly_commitment",
            "saturday_check_in",
            "user_type",
            "schedule_call",
            "will_subscribe",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]
