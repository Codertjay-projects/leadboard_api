from django.contrib import admin

# Register your models here.
from communications.models import SendGroupsEmailScheduler, SendGroupsEmailSchedulerLog, SendCustomEmailSchedulerLog, \
    SendCustomEmailScheduler


@admin.register(SendGroupsEmailScheduler)
class SendGroupsEmailSchedulerAdmin(admin.ModelAdmin):
    list_display = [
        "company",

        "email_from",
        "email_subject",
        "scheduled_date",
        "timestamp",
    ]
    search_fields = [

        "email_from",
        "email_subject",
        "scheduled_date",
        "description",
        "timestamp",
    ]


@admin.register(SendGroupsEmailSchedulerLog)
class SendGroupsEmailSchedulerLogAdmin(admin.ModelAdmin):
    list_display = [
        "company",

        "email",
        "first_name",
        "last_name",
        "view_count",
        "status",
        "timestamp",
    ]
    search_fields = [
        "email",
        "first_name",
        "last_name",
        "links_clicked",
        "status",
    ]


@admin.register(SendCustomEmailSchedulerLog)
class SendCustomEmailSchedulerLogAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "status",
        "view_count",
        "links_clicked",
        "timestamp",
    ]
    search_fields = [
        "email",
        "status",
        "view_count",
        "links_clicked",
        "timestamp",
    ]


@admin.register(SendCustomEmailScheduler)
class SendCustomEmailSchedulerAdmin(admin.ModelAdmin):
    list_display = [

        "email_subject",
        "scheduled_date",
        "timestamp",
    ]
    search_fields = [

        "email_subject",
        "email_list",
        "description",
        "scheduled_date",
        "timestamp",
    ]
