from rest_framework import serializers

from storages.models import LeadboardStorage


class LeadboardStorageSerializer(serializers.ModelSerializer):
    """
    this serializer is meant for the full crud
    """

    class Meta:
        model = LeadboardStorage
        fields = [
            "id",
            "company_id",
            "title",
            "description",
            "file",
            "link_1",
            "link_2",
            "link_3",
            "timestamp",
        ]
        read_only_fields = ["timestamp", "id", "company_id"]
