from django.contrib import admin

# Register your models here.
from .models import ScheduleCall, UserScheduleCall


@admin.register(ScheduleCall)
class ScheduleCallAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "title",
        "slug",
        "minutes",
        "meeting_link",
        "timestamp",
    ]
    search_fields = [
        "company",
        "title",
        "slug",
        "minutes",
        "meeting_link",
        "timestamp",
    ]


@admin.register(UserScheduleCall)
class UserScheduleCallAdmin(admin.ModelAdmin):
    list_display = [
        "assigned_marketer",
        "first_name",
        "last_name",
        "age_range",
        "email",
        "location",
        "gender",
        "phone",
        "age",
        "communication_medium",
        "scheduled_date",
        "employed",
        "other_training",
        "other_training_lesson",
        "will_pay",
        "income_range",
        "knowledge_scale",
        "have_laptop",
        "will_get_laptop",
        "when_get_laptop",
        "good_internet",
        "weekly_commitment",
        "saturday_check_in",
        "hours_per_week",
        "catch_up_per_hours_weeks",
        "kids_count",
        "kids_years",
        "time_close_from_school",
        "user_type",
        "eligible",
        "timestamp",
    ]
    search_fields = [
        "company",
        "assigned_marketer",
        "first_name",
        "last_name",
        "age_range",
        "email",
        "location",
        "gender",
        "phone",
        "age",
        "communication_medium",
        "scheduled_date",
        "scheduled_time",
        "employed",
        "other_training",
        "other_training_lesson",
        "will_pay",
        "income_range",
        "knowledge_scale",
        "have_laptop",
        "will_get_laptop",
        "when_get_laptop",
        "good_internet",
        "weekly_commitment",
        "saturday_check_in",
        "hours_per_week",
        "catch_up_per_hours_weeks",
        "more_details",
        "kids_count",
        "kids_years",
        "time_close_from_school",
        "user_type",
        "eligible",
        "timestamp",
    ]
