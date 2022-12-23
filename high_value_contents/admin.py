from django.contrib import admin
from .models import HighValueContent, DownloadHighValueContent


# Register your models here.

@admin.register(HighValueContent)
class HighValueContentAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "title",
        "description",
        "vimeo_link",
        "last_edit",
        "upload_date",
        "publish",
        "timestamp",
    ]
    search_fields = [

        "title",
        "description",
        "vimeo_link",
        "last_edit",
        "upload_date",
        "publish",
        "timestamp",
    ]


@admin.register(DownloadHighValueContent)
class DownloadHighValueContentAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "lead_source",
        "verified",
        "is_safe",
        "want",
        "on_leadboard",
        "timestamp",
    ]
    search_fields = [

        "first_name",
        "last_name",
        "email",
        "lead_source",
        "verified",
        "is_safe",
        "want",
        "on_leadboard",
        "timestamp",
    ]
