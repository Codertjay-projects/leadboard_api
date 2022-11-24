from django.utils import timezone
from rest_framework import serializers

from users.serializers import UserDetailSerializer
from .models import Company, Group, Industry, Location, CompanyInvite, CompanyEmployee, SendGroupsEmailScheduler, \
    SendCustomEmailScheduler


class CompanyEmployeeSerializer(serializers.ModelSerializer):
    """this is used to serialize all the marketers"""
    user = UserDetailSerializer(read_only=True)
    lead_feedbacks = serializers.SerializerMethodField(read_only=True)
    schedule_feedbacks = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompanyEmployee
        fields = [
            "id",
            "user",
            "company",
            "role",
            "lead_actions_count",
            "schedule_actions_count",
            "status",
            "timestamp",
            "lead_feedbacks",
            "schedule_feedbacks",
        ]

    def get_lead_feedbacks(self, obj: CompanyEmployee):
        """" This returns the lead feedbacks made by the user"""
        from feedbacks.serializers import FeedbackSerializer
        user = obj.user
        feedbacks = user.feedback_set.filter(content_type__model="leadcontact")
        serializer = FeedbackSerializer(feedbacks, many=True)
        return serializer.data

    def get_schedule_feedbacks(self, obj: CompanyEmployee):
        """" This returns the lead feedbacks made by the user"""
        from feedbacks.serializers import FeedbackSerializer
        user = obj.user
        # Return all feedbacks made by the user . the content_type__model enables me to get the
        #  particular model because the feedback is used for schedule and lead
        feedbacks = user.feedback_set.filter(content_type__model="userschedulecall")
        serializer = FeedbackSerializer(feedbacks, many=True)
        return serializer.data


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


class CompanyInfoSerializer(serializers.ModelSerializer):
    """
    This is  contains little info about a company
    """
    industry = IndustrySerializer()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "website",
            "phone",
            "industry",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp", ]


class CompanyModifyUserSerializer(serializers.Serializer):
    """
    This is meant to add user to the company
    """
    company_user_type = serializers.ChoiceField(choices=[("ADMIN", "ADMIN"), ("MARKETER", "MARKETER")])
    action = serializers.ChoiceField(choices=[("ACTIVATE", "ACTIVATE"), ("DEACTIVATE", "DEACTIVATE"), ])
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


class SendGroupsEmailSchedulerListSerializer(serializers.ModelSerializer):
    """
    This is used when list the the mail sent and retrieving
    """
    email_to = CompanyGroupSerializer(many=True, read_only=True)
    company = CompanyInfoSerializer(read_only=True)

    class Meta:
        model = SendGroupsEmailScheduler
        fields = [
            "id",
            "company",
            "email_to",
            "email_from",
            "email_subject",
            "scheduled_date",
            "description",
            "status",
            "timestamp",
        ]
        read_only_fields = ["id", "status", "timestamp"]


class SendGroupsEmailSchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendGroupsEmailScheduler
        fields = [
            "id",
            "email_to",
            "email_from",
            "email_subject",
            "scheduled_date",
            "description",
            "status",
            "timestamp",
        ]
        read_only_fields = ["id", "status", "timestamp"]

    def validate_scheduled_date(self, attrs):
        scheduled_date = attrs
        if scheduled_date < timezone.now():
            raise serializers.ValidationError("The schedule date must be lest than the current date")
        return scheduled_date

    def create(self, validated_data):
        # the email_to are in this form email_to=[<email_to instance>, ...] which are the instances
        # of a category
        email_to = validated_data.pop('email_to')
        instance = SendGroupsEmailScheduler.objects.create(**validated_data)
        for item in email_to:
            try:
                instance.email_to.add(item)
            except Exception as a:
                print(a)
        return instance


class SendCustomEmailListSchedulerSerializer(serializers.ModelSerializer):
    """
    This is used to send emails to custom individual
    """
    company = CompanyInfoSerializer(read_only=True)

    class Meta:
        model = SendCustomEmailScheduler
        fields = ["id",
                  "company",
                  "email_subject",
                  "email_list",
                  "description",
                  "scheduled_date",
                  "status",
                  "timestamp",
                  ]
        read_only_fields = ["id", "timestamp", "company"]


class SendCustomEmailSchedulerSerializer(serializers.ModelSerializer):
    """
    This is used to send emails to custom individual
    """

    class Meta:
        model = SendCustomEmailScheduler
        fields = "__all__"
        read_only_fields = ["id", "timestamp", "company"]

    def validate_scheduled_date(self, attrs):
        scheduled_date = attrs
        if scheduled_date < timezone.now():
            raise serializers.ValidationError("The schedule date must be lest than the current date")
        return scheduled_date
