from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ContactType, Contact, Sector, Location, CompanyStatus, CategoryOfCompany,
    Company, SeedStep, ShareType, Share, Shareholder, OurTransaction, SharePrice,
)
from .forms import (
    OurTransactionForm, CompanyForm, SeedStepForm, ShareForm, ShareholderForm,
    SharePriceForm,
)


class ContactAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'email', 'phone', 'type']


class LocationAdmin(SimpleHistoryAdmin):
    list_display = ['city', 'country']


class CompanyAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'location', 'contact', 'sector', 'status', 'category']
    form = CompanyForm


class SeedStepAdmin(SimpleHistoryAdmin):
    list_display = ['company', 'start_term', 'end_term']
    form = SeedStepForm


class ShareAdmin(SimpleHistoryAdmin):
    list_display = ['type', 'company', 'add_by']
    form = ShareForm

    def save_model(self, request, obj, form, change):
        if not obj.add_by_id:
            obj.add_by = request.user
        obj.save()


class ShareholderAdmin(SimpleHistoryAdmin):
    list_display = [
        'date', 'amount', 'owner', 'complite', 'get_share_company', 'get_share_type',
        'add_by', 'last_edit_by',
    ]
    form = ShareholderForm

    def get_share_company(self, obj):
        return obj.share.company
    
    def get_share_type(self, obj):
        return obj.share.type

    def save_model(self, request, obj, form, change):
        obj.last_edit_by = request.user
        if not obj.add_by_id:
            obj.add_by = request.user
        obj.save()

    get_share_company.admin_order_field = 'share__company'
    get_share_company.short_description = 'Company'

    get_share_type.admin_order_field = 'share__type'
    get_share_type.short_description = 'Share type'


class OurTransactionAdmin(SimpleHistoryAdmin):
    list_display = [
        'date', 'amount', 'price', 'get_share_company', 'get_share_type',
        'add_by', 'last_edit_by',
    ]
    form = OurTransactionForm

    def get_share_company(self, obj):
        return obj.share.company
    
    def get_share_type(self, obj):
        return obj.share.type

    def save_model(self, request, obj, form, change):
        obj.last_edit_by = request.user
        if not obj.add_by_id:
            obj.add_by = request.user
        super().save_model(request, obj, form, change)
        if form.cleaned_data['save_price']:
            share = obj.share
            price = obj.price
            date = obj.date
            SharePrice.objects.create(share=share, price=price, date=date)

    get_share_company.admin_order_field = 'share__company'
    get_share_company.short_description = 'Company'

    get_share_type.admin_order_field = 'share__type'
    get_share_type.short_description = 'Share type'


class SharePriceAdmin(SimpleHistoryAdmin):
    list_display = ['get_share_company', 'get_share_type', 'price', 'date']
    form = SharePriceForm

    def get_share_company(self, obj):
        return obj.share.company
    
    def get_share_type(self, obj):
        return obj.share.type

    get_share_company.admin_order_field = 'share__company'
    get_share_company.short_description = 'Company'

    get_share_type.admin_order_field = 'share__type'
    get_share_type.short_description = 'Share type'


# Register your models here.
admin.site.register(ContactType, SimpleHistoryAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Sector, SimpleHistoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(CompanyStatus, SimpleHistoryAdmin)
admin.site.register(CategoryOfCompany)
admin.site.register(Company, CompanyAdmin)
admin.site.register(SeedStep, SeedStepAdmin)
admin.site.register(ShareType, SimpleHistoryAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Shareholder, ShareholderAdmin)
admin.site.register(OurTransaction, OurTransactionAdmin)
admin.site.register(SharePrice, SharePriceAdmin)