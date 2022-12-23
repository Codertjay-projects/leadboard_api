from django.contrib import admin

from .models import Group, Company, CompanyEmployee, CompanyInvite, Industry


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "timestamp",
    ]
    search_fields = [
        "title",
        "slug",
    ]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "username",
        "company_size",
        "headquater",
        "timestamp",
    ]
    search_fields = [
        "name",
        "username",
        "website",
        "phone",
        "info_email",
        "customer_support_email",
        "overview",
        "company_size",
        "headquater",
    ]


@admin.register(CompanyEmployee)
class CompanyEmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "company",
        "role",
        "status",
        "lead_actions_count",
        "schedule_actions_count",
        "timestamp",
    ]
    search_fields = [
        "role",
        "user__first_name",
        "user__last_name",
        "status",
        "lead_actions_count",
        "schedule_actions_count",
    ]


@admin.register(CompanyInvite)
class CompanyInviteAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "invite_id",
        "email",
        "role",
        "status",
        "invited",
        "timestamp",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "invite_id",
        "email",
        "role",
        "status",
        "invited",
        "timestamp",
    ]


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "timestamp",
    ]
    search_fields = [
        "id",
        "name",
        "timestamp",
    ]
