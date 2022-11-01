from rest_framework import serializers

from newsletters.models import CompanySubscriber


class CompanySubscriberSerializer(serializers.ModelSerializer):
    """
    This enables list all subscribers, updating and retrieving
    """
    group_id = serializers.UUIDField()

    class Meta:
        model = CompanySubscriber
        fields = [
            "id",
            "company_id",
            "group_id",
            "email",
            "first_name",
            "last_name",
            "message",
            "subscribed",
            "timestamp",
        ]
        read_only_fields = ["id", "company_id", "timestamp"]


class AddToLeadBoardSerializer(serializers.Serializer):
    """
    this is used to add subscribers to leadboard.
    using list of subscribers ids
    """
    subscribers = serializers.ListField()
