import datetime
from typing import Any

from django import forms
from django.forms import formset_factory

from home.models import (
    Share, ShareType, ContactType, Contact, Company, ShareholderList,
    Shareholder,
)
from home.forms import SharePriceForm

class UploadFileForm(forms.Form):
    file = forms.FileField()


class ShareholderListExtraForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        widget=forms.HiddenInput(),
    )
    date = forms.DateField(widget=forms.widgets.NumberInput(attrs={'type':'date'}))

    def get_or_create(self):
        return ShareholderList.objects.get_or_create(
            company = self.cleaned_data['company'],
            date = self.cleaned_data['date'],
        )


class CompanySelectForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
    )


class SharePriceUpdateForm(SharePriceForm):
    consider = forms.BooleanField(required=False, initial=True)

    def save(self, commit=True) -> Any:
        if self.cleaned_data.get('consider', False):
            return super().save(commit)
        return None


class ShareholderUploadForm(forms.Form):
    name = forms.CharField()
    contact_type = forms.ModelChoiceField(
        queryset=ContactType.objects.all(),
        required=True,
        empty_label=None,
    )
    type = forms.CharField()
    amount = forms.IntegerField()
    comment = forms.CharField(max_length=10240, required=False)
    option = forms.BooleanField(initial=True, required=False)
    

    def save(self, shareholder_list: ShareholderList):
        share_type, _ = ShareType.objects.get_or_create(type=self.cleaned_data['type'])
        share, _ = Share.objects.get_or_create(type=share_type, company=shareholder_list.company)
        # Get or create contact and change contact type
        contact = Contact.objects.filter(name=self.cleaned_data['name']).first()
        if not contact:
            contact = Contact(name=self.cleaned_data['name'])
        contact.type = self.cleaned_data['contact_type']
        contact.save()
        return Shareholder.objects.create(
            shareholder_list = shareholder_list,
            contact = contact,
            share = share,
            amount = self.cleaned_data['amount'],
            option = self.cleaned_data['option'],
            comment = self.cleaned_data['comment'],
        )
    

ShareholderUploadFormSet = formset_factory(ShareholderUploadForm, extra=0)
SharePriceFormSet = formset_factory(SharePriceUpdateForm, extra=0)


class PeriodForm(forms.Form):
    reporting = forms.DateField(
        widget=forms.widgets.NumberInput(attrs={'type':'date'})
    )
    previous = forms.DateField(
        widget=forms.widgets.NumberInput(attrs={'type':'date'})
    )