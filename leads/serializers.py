from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyGroupSerializer
from companies.utils import check_group_is_under_company, get_assigned_marketer_from_company_lead
from feedbacks.serializers import FeedbackSerializer
from high_value_contents.serializers import HighValueContentSerializer
from leads.models import LeadContact
from users.serializers import UserDetailSerializer


class LeadContactUpdateCreateSerializer(serializers.ModelSerializer):
    """
    This is used to create leads
    """

    class Meta:
        model = LeadContact
        fields = [
            "id",
            "prefix",
            "groups",
            "last_name",
            "first_name",
            "email",
            "middle_name",
            "thumbnail",
            "job_title",
            "department",
            "sector",
            "want",
            "mobile",
            "high_value_content",
            "lead_source",
            "assigned_marketer",
            "verified",
            "gender",
            "category",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]


    def create(self, validated_data):
        # the groups are in this form groups=[<group instance>, ...] which are the instances
        # of a category
        global groups
        group_exists = validated_data.get("groups")
        if group_exists:
            # if the group was sent from the frontend I have to pop it out because i cant create
            # lead if it exists it would return an error
            groups = validated_data.pop('groups')
        instance = LeadContact.objects.create(**validated_data)
        ###########################################################
        """Add group if it exists on the data from the frontend"""
        if group_exists:
            for item in groups:
                # check if the user has access to using ths groups
                if not check_group_is_under_company(instance.company, item):
                    raise ValidationError("You dont have access to the groups provided")
                try:
                    instance.groups.add(item)
                except Exception as a:
                    print(a)
        ################################################################
        """ Assigned a marketer to the lead"""
        instance.assigned_marketer = get_assigned_marketer_from_company_lead(instance.company)
        instance.save()

        return instance


class LeadContactDetailSerializer(serializers.ModelSerializer):
    """
    This is meant to list all serializer for lead contact
    """
    groups = CompanyGroupSerializer(many=True)
    assigned_marketer = UserDetailSerializer(read_only=True)
    all_previous_feedbacks = serializers.SerializerMethodField(read_only=True)
    high_value_content = HighValueContentSerializer(read_only=True)

    class Meta:
        model = LeadContact
        fields = [
            "id",
            "prefix",
            "groups",
            "last_name",
            "first_name",
            "middle_name",
            "thumbnail",
            "job_title",
            "department",
            "sector",
            "want",
            "high_value_content",
            "email",
            "mobile",
            "lead_source",
            "assigned_marketer",
            "all_previous_feedbacks",
            "verified",
            "gender",
            "category",
            "timestamp",
        ]

    def get_all_previous_feedbacks(self, instance):
        #  get the previous feedback
        feedback = instance.all_previous_feedbacks()
        if feedback:
            serializer = FeedbackSerializer(feedback, many=True)
            return serializer.data
        return None
