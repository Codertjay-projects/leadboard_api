from rest_framework import serializers

from high_value_contents.models import HighValueContent


class HighValueContentSerializer(serializers.ModelSerializer):
    """
    this serializer is meant for the full crud
    """

    class Meta:
        model = HighValueContent
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
