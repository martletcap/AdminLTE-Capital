from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ContactType, Contact, Sector, Location, CompanyStatus, CategoryOfCompany,
    Company, SeedStep, ShareType, Share, Split, Shareholder, SharePrice,
)
from .forms import (
    CompanyForm, SeedStepForm, SplitForm, ShareholderForm,
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
    list_display = [
        'company', 'formatted_start_term_field', 'formatted_end_term_field',
    ]
    form = SeedStepForm

    def formatted_start_term_field(self, obj):
        return obj.start_term.strftime('%Y/%m/%d')
    
    def formatted_end_term_field(self, obj):
        return obj.end_term.strftime('%Y/%m/%d')


class ShareAdmin(SimpleHistoryAdmin):
    list_display = ['type', 'company']

class SplitAdmin(SimpleHistoryAdmin):
    list_display = ['date', 'share', 'before', 'after']
    form = SplitForm


class ShareholderAdmin(SimpleHistoryAdmin):
    list_display = [
        'formatted_date_field', 'amount', 'owner', 'complite', 'get_share_company', 'get_share_type',
    ]
    form = ShareholderForm

    def formatted_date_field(self, obj):
        return obj.date.strftime('%Y/%m/%d')

    def get_share_company(self, obj):
        return obj.share.company
    
    def get_share_type(self, obj):
        return obj.share.type

    get_share_company.admin_order_field = 'share__company'
    get_share_company.short_description = 'Company'

    get_share_type.admin_order_field = 'share__type'
    get_share_type.short_description = 'Share type'


class SharePriceAdmin(SimpleHistoryAdmin):
    list_display = [
        'get_share_company', 'get_share_type', 'price', 'formatted_date_field'
    ]
    form = SharePriceForm

    def formatted_date_field(self, obj):
        return obj.date.strftime('%Y/%m/%d')

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
admin.site.register(CategoryOfCompany, SimpleHistoryAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(SeedStep, SeedStepAdmin)
admin.site.register(ShareType, SimpleHistoryAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Split, SplitAdmin)
admin.site.register(Shareholder, ShareholderAdmin)

admin.site.register(SharePrice, SharePriceAdmin)