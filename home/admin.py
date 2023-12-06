from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Share)
admin.site.register(models.Location)
admin.site.register(models.Sector)
admin.site.register(models.Company)
admin.site.register(models.OurTransaction)