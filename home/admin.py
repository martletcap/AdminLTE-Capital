from django.contrib import admin

from .models import Share, Location, Sector, Company, OurTransaction
from .forms import OurTransactionForm

class OurTransactionAdmin(admin.ModelAdmin):
  form = OurTransactionForm



# Register your models here.
admin.site.register(Share)
admin.site.register(Location)
admin.site.register(Sector)
admin.site.register(Company)
admin.site.register(OurTransaction, OurTransactionAdmin)