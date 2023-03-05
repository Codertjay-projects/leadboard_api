from django.contrib import admin
from .models import LeadContact


@admin.register(LeadContact)
class LeadContactAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "prefix",
        "lead_type",
        "last_name",
        "first_name",
        "middle_name",
        "job_title",
        "sector",
        "email",
        "lead_source",
        "assigned_marketer",
        "is_safe",
        "verified",
        "gender",
    ]
    search_fields = [
        "lead_type",
        "last_name",
        "first_name",
        "middle_name",
        "job_title",
        "department",
        "sector",
        "email",
        "assigned_marketer__email",
    ]
