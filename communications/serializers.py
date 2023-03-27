from django.utils import timezone
from rest_framework import serializers

from communications.models import SendEmailScheduler
from companies.serializers import CompanyGroupSerializer, CompanyInfoSerializer
from schedules.serializers import ScheduleCallSerializer


class SendEmailSchedulerListSerializer(serializers.ModelSerializer):
    """
    This is used when list the  mail sent and retrieving
    """
    groups = CompanyGroupSerializer(many=True, read_only=True)
    company = CompanyInfoSerializer(read_only=True)
    schedule_calls = ScheduleCallSerializer(read_only=True)

    class Meta:
        model = SendEmailScheduler
        fields = [
            "id",
            "company",
            "message_type",
            "groups",
            "events",
            "schedule_calls",
            "high_value_contents",
            "email_list",
            "email_subject",
            "scheduled_date",
            "description",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]


class SendEmailSchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmailScheduler
        fields = [
            "id",
            "message_type",
            "groups",
            "events",
            "schedule_calls",
            "high_value_contents",
            "email_list",
            "email_subject",
            "scheduled_date",
            "description",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]

    def validate_scheduled_date(self, attrs):
        scheduled_date = attrs
        if scheduled_date < timezone.now():
            raise timezone.now()
        return scheduled_date

    def create(self, validated_data):
        # the email_to are in this form email_to=[<email_to instance>, ...] which are the instances
        # of a category
        groups = []
        events = []
        high_value_contents = []
        schedule_calls = []
        if validated_data.get("groups") or isinstance(validated_data.get("groups"), list):
            groups = validated_data.pop('groups')

        if validated_data.get("events") or isinstance(validated_data.get("events"), list):
            events = validated_data.pop('events')

        if validated_data.get("high_value_contents") or isinstance(validated_data.get("high_value_contents"), list):
            high_value_contents = validated_data.pop('high_value_contents')

        if validated_data.get("schedule_calls") or isinstance(validated_data.get("schedule_calls"), list):
            schedule_calls = validated_data.pop('schedule_calls')

        instance = SendEmailScheduler.objects.create(**validated_data)
        for item in groups:
            try:
                # you can only send to event owned by the company
                if item.company == instance.company:
                    instance.groups.add(item)
            except Exception as a:
                print(a)
        # add the events also if it was provided
        for item in events:
            try:
                # you can only send to event owned by the company
                if item.company == instance.company:
                    instance.events.add(item)
            except Exception as a:
                print(a)
        # add the high value contents also if it was provided
        for item in high_value_contents:
            try:
                # you can only send to event owned by the company
                if item.company == instance.company:
                    instance.high_value_contents.add(item)
            except Exception as a:
                print(a)
        # add the schedule_calls also if it was provided
        for item in schedule_calls:
            try:
                # you can only send to event owned by the company
                if item.company == instance.company:
                    instance.schedule_calls.add(item)
            except Exception as a:
                print(a)

        # Note this .save below is used by the logger once we have
        # successfully created this then the logger logs and sends it mail
        instance.save()
        return instance
