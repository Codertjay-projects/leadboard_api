import json

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyGroupSerializer, CompanySerializer, CompanyInfoSerializer
from companies.utils import check_group_is_under_company
from feedbacks.serializers import FeedbackSerializer
from schedules.models import UserScheduleCall, ScheduleCall
from users.serializers import UserDetailSerializer


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

    class Meta:
        model = UserScheduleCall
        fields = [
            "id",
            "assigned_marketer",
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
    company = CompanyInfoSerializer(read_only=True)
    assigned_marketer = UserDetailSerializer(read_only=True)
    previous_feedback = serializers.SerializerMethodField(read_only=True)
    group_list = serializers.SerializerMethodField(read_only=True)
    assigned_marketer_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserScheduleCall
        fields = [
            "id",
            "company",
            "groups",
            "assigned_marketer",
            "first_name",
            "last_name",
            "age_range",
            "email",
            "location",
            "gender",
            "phone",
            "age",
            "communication_medium",
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
            "group_list",
            "assigned_marketer_list",
            "schedule_call",
            "lead_contact",
            "eligible",
            "timestamp",
            "previous_feedback",
        ]
        read_only_fields = ["id", "timestamp", ]

    def get_assigned_marketer_list(self, obj: UserScheduleCall):
        """
        List of marketers currently on company .
        It won't show the admin or owner with in the list
        :param obj: LeadContact
        :return: marketer_list dictionary
        """
        try:
            marketer_info_list = obj.company.companyemployee_set.filter(
                role="MARKETER", status="ACTIVE").values_list(
                "user__id",
                "user__first_name",
                "user__last_name", )
            # Initialize a list for the user ids
            datasets = []
            for item in marketer_info_list:
                checked = False
                if not item[0]:
                    # sometimes it can be none
                    continue
                if item[0] == obj.assigned_marketer.id:
                    # If the marketer id is within then we know he is the current one
                    checked = True
                json_item = {
                    'id': str(item[0]),
                    'first_name': item[1],
                    'last_name': item[2],
                    'status': checked
                }
                # append the item to the list
                datasets.append(json_item)
            return datasets
        except Exception as a:
            print(a)
            return None

    def get_group_list(self, obj: UserScheduleCall):
        """
        List of groups in the db
        Return status if category selected in UserScheduleCall
        """
        datasets = []
        for c in obj.company.group_set.all():
            # Get all groups currently on this company
            # ( Reason why I use the company is to make it little more fast)
            if c in obj.groups.all():
                checked = True  # Checked categories
            else:
                checked = False
            json_item = {
                'id': str(c.id),
                'title': c.title,
                'status': checked
            }
            # append the item to the list
            datasets.append(json_item)
        return datasets

    def get_previous_feedback(self, instance):
        #  get the previous feedback
        feedback = instance.previous_feedback()
        if feedback:
            serializer = FeedbackSerializer(feedback)
            return serializer.data
        return None
