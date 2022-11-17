from rest_framework import serializers

from high_value_contents.models import HighValueContent, DownloadHighValueContent


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
            "slug",
            "description",
            "thumbnail",
            "pdf_file",
            "youtube_link",
            "vimeo_link",
            "vimeo_hash_key",
            "schedule_link",
            "last_edit",
            "upload_date",
            "publish",
            "timestamp",
        ]
        read_only_fields = ["timestamp", "id", "company_id", "last_edit", "upload_date"]


class DownloadHighValueContentSerializer(serializers.ModelSerializer):
    """
    this only contain fields which could be used to add to the lead and also send the user
    """

    class Meta:
        model = DownloadHighValueContent
        fields = "__all__"
        read_only_fields = ["id", "verified", "is_safe", "timestamp"]
