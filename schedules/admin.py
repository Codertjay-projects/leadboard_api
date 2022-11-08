from django.contrib import admin

# Register your models here.
from .models import ScheduleCall,UserScheduleCall

admin.site.register(ScheduleCall)
admin.site.register(UserScheduleCall)