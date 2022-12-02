from django.contrib import admin

from .models import Group, Company, CompanyEmployee, CompanyInvite, Industry

admin.site.register(Group)
admin.site.register(Company)
admin.site.register(CompanyEmployee)

admin.site.register(CompanyInvite)
admin.site.register(Industry)
