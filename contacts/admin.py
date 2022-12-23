from django.contrib import admin
from .models import ContactUs, Newsletter


# Register your models here.


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = [
        "company",

        "email",
        "first_name",
        "last_name",
        "message",
        "on_leadboard",
        "timestamp",
    ]
    search_fields = [

        "email",
        "first_name",
        "last_name",
        "message",
        "on_leadboard",
        "timestamp",
    ]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = [
        "company",

        "email",
        "on_blog",
        "timestamp",
    ]
    search_fields = [

        "email",
        "on_blog",
        "timestamp",
    ]

