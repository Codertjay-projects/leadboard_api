from django.contrib import admin

# Register your models here.
from .models import Event,EventRegister

admin.site.register(Event)
admin.site.register(EventRegister)