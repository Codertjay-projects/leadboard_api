from rest_framework import serializers

from .models import ContactUs, Newsletter, UnSubscriber


class ContactUsSerializer(serializers.ModelSerializer):
    """
    This enables list all contactus info, updating and retrieving
    """

    class Meta:
        model = ContactUs
        fields = [
            "id",
            "company_id",
            "group_id",
            "email",
            "first_name",
            "last_name",
            "message",
            "timestamp",
        ]
        read_only_fields = ["id", "company_id", "group_id", "timestamp"]


class AddToLeadBoardSerializer(serializers.Serializer):
    """
    this is used to add contactus to leadboard.
    using list of contactus_infos ids
    """
    contactus_infos = serializers.ListField()


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "company",
            "email",
            "on_blog",
            "timestamp",
        ]
        model = Newsletter
        read_only_fields = ["id", "company", "timestamp"]


class UnSubscriberSerializer(serializers.ModelSerializer):
    """
    This is used to list all users that unsubsribe and does not want to recieve email
    """
    email = serializers.EmailField(required=False)

    class Meta:
        model = UnSubscriber
        fields = [
            "id",
            "company",
            "email",
            "message",
            "timestamp",
        ]
        read_only_fields = ["id", "company", "timestamp"]
