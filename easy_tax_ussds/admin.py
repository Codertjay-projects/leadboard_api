from django.contrib import admin

# Register your models here.
from easy_tax_ussds.models import EasyTaxUSSDState, EasyTaxUSSDLGA, EasyTaxUSSD


@admin.register(EasyTaxUSSDState)
class EasyTaxUSSDStateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'timestamp']
    search_fields = ['id', 'name', 'timestamp']


@admin.register(EasyTaxUSSDLGA)
class EasyTaxUSSDLGAAdmin(admin.ModelAdmin):
    list_display = ['id', 'state', 'name']
    search_fields = ['id', 'state__name', 'name']


@admin.register(EasyTaxUSSD)
class EasyTaxUSSDAdmin(admin.ModelAdmin):
    list_display = ["full_name",
                    "phone_number",
                    "tax_payer_identification",
                    "balance",
                    "year_of_birth",
                    "gender",
                    "lga",
                    "timestamp", ]
    search_fields = [
        "full_name",
        "phone_number",
        "tax_payer_identification",
        "balance",
        "year_of_birth",
        "gender",
        "lga",
        "timestamp", ]
