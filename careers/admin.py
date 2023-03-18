from django.contrib import admin
from .models import Applicant, Job

# Register your models here.



@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "email",
        "last_name",
        "status",
        "nationality",
        "country_of_residence",
        "timestamp",
    ]
    search_fields = [
        "first_name",
        "email",
        "last_name",
        "status",
        "nationality",
        "country_of_residence",
        "timestamp",
    ]




@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "job_category",
        "job_experience_level",
        "title",
        "application_deadline",
        "timestamp",
    ]
    search_fields = [
        "job_category",
        "job_experience_level",
        "title",
        "description",
        "application_deadline",
        "timestamp",
    ]
