from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from companies.serializers import CompanyGroupSerializer
from companies.utils import check_group_is_under_company
from feedbacks.serializers import FeedbackSerializer
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
            "mobile",
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
        groups = validated_data.pop('groups')
        instance = LeadContact.objects.create(**validated_data)
        for item in groups:
            # check if the user has access to using ths groups
            if not check_group_is_under_company(instance.company, item):
                raise ValidationError("You dont have access to the groups provided")
            try:
                instance.groups.add(item)
            except Exception as a:
                print(a)
        return instance


class LeadContactSerializer(serializers.ModelSerializer):
    """
    This is meant to list all serializer for leadconact
    """
    groups = CompanyGroupSerializer(many=True)
    assigned_marketer = UserDetailSerializer(read_only=True)
    previous_feedback = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LeadContact
        fields = [
            "id",
            "prefix",
            "groups",
            "staff",
            "last_name",
            "first_name",
            "email",
            "mobile",
            "lead_source",
            "assigned_marketer",
            "previous_feedback",
            "verified",
            "gender",
            "category",
            "timestamp",
        ]

    def get_previous_feedback(self, instance):
        #  get the previous feedback
        feedback = instance.previous_feedback()
        if feedback:
            serializer = FeedbackSerializer(feedback)
            return serializer.data
        return None
