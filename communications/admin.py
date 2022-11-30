from django.contrib import admin

# Register your models here.
from communications.models import SendGroupsEmailScheduler, SendGroupsEmailSchedulerLog, SendCustomEmailSchedulerLog, \
    SendCustomEmailScheduler

admin.site.register(SendGroupsEmailScheduler)
admin.site.register(SendGroupsEmailSchedulerLog)
admin.site.register(SendCustomEmailSchedulerLog)
admin.site.register(SendCustomEmailScheduler)
