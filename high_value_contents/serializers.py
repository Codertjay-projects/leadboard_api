from rest_framework import serializers

import high_value_contents
from high_value_contents.models import HighValueContent, DownloadHighValueContent
from users.serializers import UserSerializer


class HighValueContentSerializer(serializers.ModelSerializer):
    """
    this serializer is meant for the full crud
    """
    slug = serializers.SlugField(required=False)
    file_extension = serializers.SerializerMethodField(read_only=True)
    file_size = serializers.SerializerMethodField(read_only=True)
    created_by = UserSerializer(read_only=True)
    last_edit_by = UserSerializer(read_only=True)

    class Meta:
        model = HighValueContent
        fields = [
            "id",
            "company_id",
            "group",
            "created_by",
            "last_edit_by",
            "title",
            "slug",
            "description",
            "thumbnail",
            "pdf_file",
            "link",
            "youtube_link",
            "vimeo_link",
            "vimeo_hash_key",
            "schedule_link",
            "last_edit",
            "file_extension",
            "file_size",
            "upload_date",
            "publish",
            "timestamp",
        ]
        read_only_fields = ["timestamp", "id", "company_id", "file_extension", "file_size", "created_by",
                            "last_edit_by",
                            "last_edit", "upload_date",
                            "group"]

    def get_file_extension(self, obj):
        file_extension = obj.pdf_file.name
        if file_extension:
            return file_extension.split(".")[-1]
        return None

    def get_file_size(self, obj:HighValueContent):
        file = obj.pdf_file
        if file:
            # Convert the file size to megabytes
            file_size_megabytes = file.size / 1048576
            return file_size_megabytes
        return None


class DownloadHighValueContentSerializer(serializers.ModelSerializer):
    """
    this only contain fields which could be used to add to the lead and also send the user
    """

    class Meta:
        model = DownloadHighValueContent
        fields = "__all__"
        read_only_fields = ["id", "verified", "is_safe", "timestamp"]


class DownloadHighValueContentDetailSerializer(serializers.ModelSerializer):
    """
    this is only used to get the detail of the user that need the content and also the content info
    """
    high_value_content = HighValueContentSerializer(read_only=True)

    class Meta:
        model = DownloadHighValueContent
        fields = "__all__"
