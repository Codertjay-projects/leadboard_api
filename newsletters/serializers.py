from rest_framework import serializers

from newsletters.models import CompanySubscriber


class CompanySubscriberSerializer(serializers.ModelSerializer):
    """
    This enables list all subscribers, updating and retrieving
    """
    class Meta:
        model = CompanySubscriber
        fields = [
            "id",
            "company_id",
            "group_id",
            "email",
            "subscribed",
            "timestamp",
        ]
        read_only_fields = ["id", "company_id", "timestamp"]