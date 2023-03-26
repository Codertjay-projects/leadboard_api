from django.contrib import admin

from .models import HighValueContent


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


