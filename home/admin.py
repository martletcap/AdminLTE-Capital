import sys

from django.urls import reverse
from django.contrib import admin
from django.db.models import Sum
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ContactType, Contact, Sector, Location, CompanyStatus, CategoryOfCompany,
    Company, SeedStep, ShareType, Share, Split, SharePrice,
    MoneyTransaction, ShareTransaction, Percent, FairValueList, 
    FairValueMethod, ShareholderList, Shareholder, CompanyHouseParser,
)
from .forms import (
    CompanyForm, SeedStepForm, SplitForm,
    SharePriceForm, MoneyTransactionForm, ShareTransactionForm,
    PercentForm, FairValueListForm, ShareholderListForm, ShareholderForm,
)

class SimpleHistoryAdminCustom(SimpleHistoryAdmin):
    list_max_show_all = sys.maxsize


class ContactAdmin(SimpleHistoryAdminCustom):
    list_display = ['name', 'email', 'phone', 'type']


class LocationAdmin(SimpleHistoryAdminCustom):
    list_display = ['city', 'country']


class CompanyAdmin(SimpleHistoryAdminCustom):
    list_display = ['name', 'location', 'contact', 'staff', 'sector', 'status', 'category']
    form = CompanyForm


class SeedStepAdmin(SimpleHistoryAdminCustom):
    list_display = [
        'company', 'formatted_start_term_field', 'formatted_end_term_field',
    ]
    form = SeedStepForm

    def formatted_start_term_field(self, obj):
        return obj.start_term.strftime('%Y/%m/%d')
    
    def formatted_end_term_field(self, obj):
        return obj.end_term.strftime('%Y/%m/%d')


class ShareAdmin(SimpleHistoryAdminCustom):
    list_display = ['type', 'company']


class SplitAdmin(SimpleHistoryAdminCustom):
    list_display = ['date', 'share', 'before', 'after']
    form = SplitForm


class SharePriceAdmin(SimpleHistoryAdminCustom):
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


class ShareTransactionAdmin(SimpleHistoryAdminCustom):
    change_form_template = 'pages/sharetransaction_change_form.html'
    list_display = [
        'get_money_transaction', 'formatted_date_field', 'share', 'amount',
    ]
    form = ShareTransactionForm

    def get_money_transaction(self, obj):
        return obj.money_transaction.price
    
    def formatted_date_field(self, obj):
        return obj.date.strftime('%Y/%m/%d')

    def add_view(self, request, form_url="", extra_context=None):
        if extra_context is None: extra_context = {}
        extra_context['show_save_and_add_prices'] = True
        return super().add_view(request, form_url, extra_context)
    
    def response_post_save_add(self, request, obj):        
        if "_saveandaddprices" in request.POST:
            price = obj.money_transaction.price/obj.amount
            return redirect(
                reverse('update_prices')+'?'+
                f'company={obj.share.company.id}'+ '&' +
                f'price={price}' + '&' + 
                f'date={obj.date}'
            )
        return super().response_post_save_add(request, obj)


class MoneyTransactionAdmin(SimpleHistoryAdminCustom):
    list_display = [
        'formatted_date_field', 'price', 'company', 'transaction_type',
        'portfolio',
    ]
    form = MoneyTransactionForm

    def formatted_date_field(self, obj):
        return obj.date.strftime('%Y/%m/%d')
    
    def add_view(self, request, form_url="", extra_context=None):
        if extra_context is None: extra_context = {}
        extra_context['show_save_and_add_share'] = True
        return super().add_view(request, form_url, extra_context)
    
    def response_post_save_add(self, request, obj):        
        if "_saveandaddshare" in request.POST:
            share_transaction_url = reverse('admin:home_sharetransaction_add')
            return redirect(
                share_transaction_url + '?'+ 
                f'money_transaction={obj.pk}' + '&' + f'date={obj.date}'
            )
        return super().response_post_save_add(request, obj)
    
    def get_changeform_initial_data(self, request):
        return {'portfolio': 2} # Martlet default portfolio
    

class PercentAdmin(SimpleHistoryAdminCustom):
    list_display = ['name', 'percent']
    form = PercentForm


class FairValueListAdmin(SimpleHistoryAdminCustom):
    list_display = ['formatted_date_field', 'comment']
    form = FairValueListForm
    add_form_template = 'admin/change_form.html'
    change_form_template = 'pages/fairvaluelist_change_form.html'

    def formatted_date_field(self, obj):
        return obj.date.strftime('%Y/%m/%d')
    
    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        context['result_headers'] = [
            'Company', 'Percent', 'Color', 'Comment',
        ]
        context['results'] = []
        context['links'] = []
        fair_value_methods = FairValueMethod.objects.filter(
            fair_value_list = obj,
        ).select_related()
        for fair_value_method in fair_value_methods:
            context['links'].append(
                reverse(
                    f'admin:{FairValueMethod._meta.app_label}_{FairValueMethod._meta.model_name}_change',
                    kwargs = {'object_id':fair_value_method.pk},
                )
            )
            context['results'].append((
                fair_value_method.company, fair_value_method.percent,
                fair_value_method.color, fair_value_method.comment,
            ))
        context['id'] = obj.pk if obj else obj
        return super().render_change_form(request, context, add, change, form_url, obj)
    

class FairValueMethodAdmin(SimpleHistoryAdminCustom):
    list_display = ['company', 'percent']


class ShareholderListAdmin(SimpleHistoryAdminCustom):
    list_display = [
        'company', 'formatted_date_field', 'shares_field', 'options_field'
    ]
    form = ShareholderListForm
    add_form_template = 'admin/change_form.html'
    change_form_template = 'pages/shareholderlist_change_form.html'

    def formatted_date_field(self, obj):
        return obj.date.strftime('%Y/%m/%d')
    
    def shares_field(self, obj):
        total = Shareholder.objects.filter(
            shareholder_list = obj,
            option = True,
        ).aggregate(total_amount = Sum('amount'))['total_amount']
        return total
    
    def options_field(self, obj):
        total = Shareholder.objects.filter(
            shareholder_list = obj,
            option = False,
        ).aggregate(total_amount = Sum('amount'))['total_amount']
        return total
    
    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        context['result_headers'] = [
            'Contact', 'Type', 'Share', 'Amount', 'Share',
        ]
        context['results'] = []
        context['links'] = []
        shareholders = Shareholder.objects.filter(
            shareholder_list = obj,
        ).select_related('contact__type', 'share__type')
        for shareholder in shareholders:
            context['links'].append(
                reverse(
                    f'admin:{Shareholder._meta.app_label}_{Shareholder._meta.model_name}_change',
                    kwargs = {'object_id':shareholder.pk},
                )
            )
            context['results'].append((
                shareholder.contact, shareholder.contact.type,
                shareholder.share.type, shareholder.amount, shareholder.option,
            ))
        context['id'] = obj.pk if obj else obj
        return super().render_change_form(request, context, add, change, form_url, obj)
    

    shares_field.short_description = 'Shares'
    options_field.short_description = 'Options'


class ShareholderAdmin(SimpleHistoryAdminCustom):
    change_form_template = 'pages/shareholder_change_form.html'
    list_display = ['shareholder_list', 'contact', 'share', 'amount', 'option']
    list_select_related = ('shareholder_list', 'contact', 'share')
    form = ShareholderForm

class CompanyHouseParserAdmin(SimpleHistoryAdmin):
    list_display = [
        'company', 'formatted_parsing_datetime_field', 'formatted_file_date',
        'parsed_field', 'status', 'shares_field', 'file_link_field', 'comment',
    ]
    change_form_template = 'pages/companyhouseparse_change_form.html'
    change_list_template = 'pages/companyhouseparser_change_list.html'

    def shares_field(self, obj):
        shareholder_list = obj.shareholder_list
        if shareholder_list is None:
            return 0
        sum = Shareholder.objects.filter(
            shareholder_list=shareholder_list,
            option = True,
        ).aggregate(total_amount=Sum('amount'))['total_amount']
        return sum

    def file_link_field(self, obj):
        link = "<a href='https://find-and-update.company-information.service.gov.uk/company/{0}/filing-history/{1}/document?format=pdf&download=1'>Link</a>"
        return mark_safe(link.format(obj.company.number, obj.transaction_id))
    
    def parsed_field(self, obj):
        if obj.shareholder_list:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')
    
    def formatted_parsing_datetime_field(self, obj):
        return obj.parsing_datetime.strftime('%Y/%m/%d %H:%M')
    
    def formatted_file_date(self, obj):
        return obj.file_date.strftime('%Y/%m/%d')
    

    # shares_field
    shares_field.short_description = 'Shares amount'
    # file link
    file_link_field.short_description = 'Download'
    # parsed field
    parsed_field.short_description = 'Parsed'
    # parsing datetime field
    formatted_parsing_datetime_field.short_description = 'Parsing DateTime'
    # file date field
    formatted_file_date.short_description = 'File Date'


# Register your models here.
admin.site.register(ContactType, SimpleHistoryAdminCustom)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Sector, SimpleHistoryAdminCustom)
admin.site.register(Location, LocationAdmin)
admin.site.register(CompanyStatus, SimpleHistoryAdminCustom)
admin.site.register(CategoryOfCompany, SimpleHistoryAdminCustom)
admin.site.register(Company, CompanyAdmin)
admin.site.register(SeedStep, SeedStepAdmin)
admin.site.register(ShareType, SimpleHistoryAdminCustom)
admin.site.register(Share, ShareAdmin)
admin.site.register(Split, SplitAdmin)
admin.site.register(SharePrice, SharePriceAdmin)
admin.site.register(MoneyTransaction, MoneyTransactionAdmin)
admin.site.register(ShareTransaction, ShareTransactionAdmin)
admin.site.register(Percent, PercentAdmin)
admin.site.register(FairValueList, FairValueListAdmin)
admin.site.register(FairValueMethod, FairValueMethodAdmin)
admin.site.register(ShareholderList, ShareholderListAdmin)
admin.site.register(Shareholder, ShareholderAdmin)
admin.site.register(CompanyHouseParser, CompanyHouseParserAdmin)