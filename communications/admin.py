from django.contrib import admin

# Register your models here.
from communications.models import SendEmailScheduler


@admin.register(SendEmailScheduler)
class SendEmailSchedulerAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "message_type",
        "email_subject",
        "scheduled_date",
        "timestamp",
    ]
    search_fields = [

        "email_subject",
        "scheduled_date",
        "description",
        "timestamp",
    ]
