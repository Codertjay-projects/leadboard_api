from django.contrib import admin
from .models import  JobType,Applicant,Job
# Register your models here.

admin.site.register(JobType)
admin.site.register(Applicant)
admin.site.register(Job)