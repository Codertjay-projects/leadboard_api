from rest_framework import serializers

from companies.serializers import CompanyGroupSerializer
from leads.models import LeadContact
from users.serializers import UserSerializer
from companies.utils import check_marketer_and_admin_access_group


class LeadUpdateCreateSerializer(serializers.ModelSerializer):
    """
    This is used to create leads
    """
    assigned_marketer = UserSerializer()

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
        # the groups is in this form groups=[<group instance>, ...] which are the instances
        # of a category
        groups = validated_data.pop('groups')
        instance = LeadContact.objects.create(**validated_data)
        for item in groups:
            # check if the user has access
            if not check_marketer_and_admin_access_group(user, item):
                raise ValidationError("You dont have access to the groups provided")
            try:
                instance.groups.add(item)
            except Exception as a:
                print(a)
        return instance


class LeadContactListSerializer(serializers.ModelSerializer):
    """
    This is meant to list all serializer for leadconact
    """
    groups = CompanyGroupSerializer(many=True)
    assigned_marketer = UserSerializer()

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
            "verified",
            "gender",
            "category",
            "timestamp",
        ]
