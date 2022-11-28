from django.contrib import admin

from .models import Group, Company, CompanyEmployee, CompanyInvite, Industry
from communications.models import SendGroupsEmailSchedulerLog, SendGroupsEmailScheduler

admin.site.register(Group)
admin.site.register(Company)
admin.site.register(CompanyEmployee)
admin.site.register(SendGroupsEmailScheduler)
admin.site.register(SendGroupsEmailSchedulerLog)
admin.site.register(CompanyInvite)
admin.site.register(Industry)
