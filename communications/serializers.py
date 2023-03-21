from django.utils import timezone
from rest_framework import serializers

from communications.models import SendEmailScheduler
from companies.serializers import CompanyGroupSerializer, CompanyInfoSerializer


class SendGroupsEmailSchedulerListSerializer(serializers.ModelSerializer):
    """
    This is used when list the the mail sent and retrieving
    """
    email_to = CompanyGroupSerializer(many=True, read_only=True)
    company = CompanyInfoSerializer(read_only=True)

    class Meta:
        model = SendEmailScheduler
        fields = [
            "id",
            "company",
            "email_to",
            "email_from",
            "email_subject",
            "scheduled_date",
            "description",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]


class SendGroupsEmailSchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmailScheduler
        fields = [
            "id",
            "email_to",
            "email_from",
            "email_subject",
            "scheduled_date",
            "description",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]

    def validate_scheduled_date(self, attrs):
        scheduled_date = attrs
        if scheduled_date < timezone.now():
            raise serializers.ValidationError("The schedule date must be greater than the current date")
        return scheduled_date

    def create(self, validated_data):
        # the email_to are in this form email_to=[<email_to instance>, ...] which are the instances
        # of a category
        email_to = []
        if validated_data.get("email_to"):
            email_to = validated_data.pop('email_to')
        instance = SendEmailScheduler.objects.create(**validated_data)
        instance.message_type = "GROUP"
        for item in email_to:
            try:
                instance.groups.add(item)
            except Exception as a:
                print(a)
        # Note this .save below is used by the logger once we have
        # successfully created this then the logger logs and sends it mail
        instance.save()
        return instance


class SendCustomEmailListSchedulerSerializer(serializers.ModelSerializer):
    """
    This is used to send emails to custom individual
    """
    company = CompanyInfoSerializer(read_only=True)

    class Meta:
        model = SendEmailScheduler
        fields = ["id",
                  "company",
                  "email_subject",
                  "email_list",
                  "description",
                  "scheduled_date",
                  "timestamp",
                  ]
        read_only_fields = ["id", "timestamp", "company"]


class SendCustomEmailSchedulerSerializer(serializers.ModelSerializer):
    """
    This is used to send emails to custom individual
    """
    message_type = serializers.CharField(max_length=250, required=False)

    class Meta:
        model = SendEmailScheduler
        fields = [
            "message_type",
            "email_list",
            "email_subject",
            "scheduled_date",
            "description",
        ]
        read_only_fields = ["id", "timestamp", "company"]

    def validate_scheduled_date(self, attrs):
        scheduled_date = attrs
        if scheduled_date < timezone.now():
            raise serializers.ValidationError("The schedule date must be greater than the current date")
        return scheduled_date

