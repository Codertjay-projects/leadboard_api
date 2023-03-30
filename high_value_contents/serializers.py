from rest_framework import serializers

from high_value_contents.models import HighValueContent, LEAD_SOURCE
from leads.models import LeadContact
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
    download_count = serializers.SerializerMethodField(read_only=True)

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
            "file",
            "link",
            "youtube_link",
            "vimeo_link",
            "vimeo_hash_key",
            "schedule_link",
            "last_edit",
            "file_extension",
            "download_count",
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
        file_extension = obj.file.name
        if file_extension:
            return file_extension.split(".")[-1]
        return None

    def get_file_size(self, obj: HighValueContent):
        file = obj.file
        try:
            # Convert the file size to megabytes
            file_size_megabytes = file.size / 1048576
            return round(file_size_megabytes, 2)
        except:
            return None

    def get_download_count(self, obj: HighValueContent):
        return obj.lead_contacts.count()


class DownloadHighValueContentSerializer(serializers.Serializer):
    """
    this only contain fields which could be used to add to the lead and also send the user
    """
    high_value_content = serializers.UUIDField()
    first_name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    email = serializers.EmailField()
    lead_source = serializers.ChoiceField(choices=LEAD_SOURCE)
    want = serializers.CharField(max_length=1000)


class DownloadHighValueContentDetailSerializer(serializers.ModelSerializer):
    """
    this is only used to get the detail of the user that need the content and also the content info
    """

    class Meta:
        model = LeadContact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "lead_source",
            "verified",
            "is_safe",
            "want",
            "timestamp",
        ]


class HighValueContentBasicSerializer(serializers.ModelSerializer):
    """
    this serializer is meant for send email grouping
    """

    class Meta:
        model = HighValueContent
        fields = [
            "id",
            "title",
            "company",
        ]