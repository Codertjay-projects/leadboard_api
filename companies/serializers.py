from rest_framework import serializers

from users.serializers import UserDetailSerializer
from .models import Company, Group, Industry, Location, CompanyInvite, CompanyMarketer, CompanyEmployee


class CompanyEmployeeSerializer(serializers.ModelSerializer):
    """this is used to serialize all the marketers"""
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = CompanyEmployee
        fields = [
            "id",
            "user",
            "company",
            "role",
            "status",
            "timestamp",
        ]


class IndustrySerializer(serializers.ModelSerializer):
    """
    this is used to list the industry , create, update
    """

    class Meta:
        model = Industry
        fields = [
            "id",
            "name",
            "timestamp",
        ]

        read_only_fields = ["id", "timestamp", ]


class LocationSerializer(serializers.ModelSerializer):
    """
    this is used to create location , list location and update the location
    """

    class Meta:
        model = Location
        fields = [
            "id",
            "state",
            "country",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]


class CompanyCreateUpdateSerializer(serializers.ModelSerializer):
    """
    This is used to create a company  .
    """

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "website",
            "phone",
            "info_email",
            "customer_support_email",
            "industry",
            "overview",
            "company_size",
            "headquater",
            "founded",
            "locations",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]

    def create(self, validated_data):
        # the locations are in this form locations=[<locations instance>, ...] which are the instances
        # of a category
        locations = validated_data.pop('locations')
        instance = Company.objects.create(**validated_data)
        for item in locations:
            try:
                instance.locations.add(item)
            except Exception as a:
                print(a)
        return instance


class CompanySerializer(serializers.ModelSerializer):
    """
    This is used to list all  company's or get the detail .
    """
    owner = UserDetailSerializer(read_only=True)
    locations = LocationSerializer(many=True)
    industry = IndustrySerializer()
    company_employees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "owner",
            "name",
            "website",
            "phone",
            "info_email",
            "customer_support_email",
            "industry",
            "overview",
            "company_size",
            "headquater",
            "founded",
            "locations",
            "timestamp",
            "company_employees",
        ]
        read_only_fields = ["id", "timestamp", "company_employees"]

    def get_company_employees(self, obj):
        """"This is used to list all company employees """
        serializer = CompanyEmployeeSerializer(obj.company_employees(), many=True)
        return serializer.data


class CompanyAddUserSerializer(serializers.Serializer):
    """
    This is meant to add user to the company
    """
    company_user_type = serializers.ChoiceField(choices=[("ADMIN", "ADMIN"), ("MARKETER", "MARKETER")])
    action = serializers.ChoiceField(choices=[("ADD", "ADD"), ("DELETE", "DELETE"), ])
    email = serializers.EmailField()


class CompanyGroupSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to create a group under a company
    """

    class Meta:
        model = Group
        fields = [
            "id",
            "title",
            "slug",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", "slug"]


class CompanyInviteSerializer(serializers.ModelSerializer):
    """
    this serializer is meant to create an invitation for a user to JOIN
    """

    class Meta:
        model = CompanyInvite
        fields = [
            "id",
            "first_name",
            "invite_id",
            "email",
            "role",
            "status",
            "timestamp",
        ]
        read_only_fields = ["invite_id", "timestamp", "status"]
