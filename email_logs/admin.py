from django.contrib import admin

from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "message_type",
        "email_to",
        "max_retries",
        "error",
        "status",
        "timestamp",
    ]
    search_fields = [

        "message_type",
        "email_to",
        "max_retries",
        "error",
        "status",
    ]
