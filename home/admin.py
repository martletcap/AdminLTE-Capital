from django.contrib import admin

from .models import Share, Location, Sector, Company, OurTransaction
from .forms import OurTransactionForm, CompanyForm

class OurTransactionAdmin(admin.ModelAdmin):
  list_display = ["company", "date", "amount", "price", "total", "share"]
  form = OurTransactionForm

class CompanyAdmin(admin.ModelAdmin):
  list_display = ["name", "location", "sector"]
  form = CompanyForm

# Register your models here.
admin.site.register(Share)
admin.site.register(Location)
admin.site.register(Sector)
admin.site.register(Company, CompanyAdmin)
admin.site.register(OurTransaction, OurTransactionAdmin)