from django.contrib import admin

from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        "company",

        "message_id",
        "message_type",
        "email_from",
        "email_to",
        "reply_to",
        "max_retries",
        "email_subject",
        "description",
        "error",
        "scheduled_date",
        "status",
        "timestamp",
    ]
    search_fields = [

        "message_id",
        "message_type",
        "email_from",
        "email_to",
        "reply_to",
        "max_retries",
        "email_subject",
        "description",
        "error",
        "scheduled_date",
        "status",
    ]
