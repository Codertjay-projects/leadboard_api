from django.contrib import admin

# Register your models here.
from .models import UserProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "verified",
        "date_joined",
        "timestamp",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "verified",
        "date_joined",
        "timestamp",
    ]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "gender",
        "date_of_birth",
        "address",
        "nationality",
        "country",
        "city",
        "timestamp",
    ]
    search_fields = [
        "gender",
        "date_of_birth",
        "address",
        "description",
        "nationality",
        "country",
        "city",
        "timestamp",
    ]
