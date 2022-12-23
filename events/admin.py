from django.contrib import admin

# Register your models here.
from .models import Event, EventRegister


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "email",
        "title",
        "tags",
        "price",
        "start_date",
        "end_date",
        "is_paid",
        "timestamp",
    ]
    search_fields = [

        "email",
        "title",
        "slug",
        "description",
        "location",
        "link_1",
        "link_2",
        "tags",
        "price",
        "start_date",
        "end_date",
        "is_paid",
        "timestamp",
    ]


@admin.register(EventRegister)
class EventRegisterAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "mobile",
        "gender",
        "age_range",
        "will_receive_email",
        "accept_terms_and_conditions",
        "timestamp",
    ]
    search_fields = [

        "first_name",
        "last_name",
        "email",
        "mobile",
        "gender",
        "age_range",
        "will_receive_email",
        "accept_terms_and_conditions",
        "timestamp",
    ]
