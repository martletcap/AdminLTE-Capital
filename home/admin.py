from django.contrib import admin

from .models import (
    ContactType, Contact, Location, Sector, CompanyStatus, CategoryOfCompany,
    Company, ShareType, SeedStep, Share, Shareholder, OurTransaction, SharePrice,
)
from .forms import (
    OurTransactionForm, CompanyForm, SeedStepForm, ShareholderForm,
    SharePriceForm,
)

class OurTransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "amount", "price", "share"]
    form = OurTransactionForm

class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "sector"]
    form = CompanyForm

class SeedStepAdmin(admin.ModelAdmin):
    list_display = ['company', 'start_term', 'end_term']
    form = SeedStepForm

class ShareholderAdmin(admin.ModelAdmin):
    list_display = ['date', 'owner', 'amount', 'share']
    form = ShareholderForm

class SharePriceAdmin(admin.ModelAdmin):
    list_display = ['share', 'price', 'date']
    form = SharePriceForm

# Register your models here.
admin.site.register(ContactType)
admin.site.register(Contact)
admin.site.register(Location)
admin.site.register(Sector)
admin.site.register(CompanyStatus)
admin.site.register(CategoryOfCompany)
admin.site.register(Company, CompanyAdmin)
admin.site.register(ShareType)
admin.site.register(SeedStep, SeedStepAdmin)
admin.site.register(Share)
admin.site.register(Shareholder, ShareholderAdmin)
admin.site.register(OurTransaction, OurTransactionAdmin)
admin.site.register(SharePrice, SharePriceAdmin)