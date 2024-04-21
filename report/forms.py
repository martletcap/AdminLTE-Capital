import datetime
from typing import Any

from django import forms
from django.forms import formset_factory

from home.models import (
    COLOR_CHOICES, Share, ShareType, ContactType, Contact, Company,
    ShareholderList, Shareholder, Percent, FairValueMethod,
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
    previous = forms.DateField(
        widget=forms.widgets.NumberInput(attrs={'type':'date'})
    )
    reporting = forms.DateField(
        widget=forms.widgets.NumberInput(attrs={'type':'date'})
    )

class DateForm(forms.Form):
    date = forms.DateField(
        widget=forms.widgets.NumberInput(attrs={'type':'date'})
    )

class SharesControlForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=True,
        empty_label=None,
    )
    shares = forms.IntegerField(required=True, min_value=0, initial=0)
    options = forms.IntegerField(required=True, min_value=0, initial=0)

    def create(self, date):
        initial_data = []
        # Collision check
        collision = ShareholderList.objects.filter(
            company = self.cleaned_data['company'],
            date = date,
        ).first()
        if collision: return None
        shareholder_list = ShareholderList.objects.filter(
            company = self.cleaned_data['company'],
            date__lt = date,
        ).order_by('-date')[:1].first()
        shareholders = Shareholder.objects.filter(
            shareholder_list = shareholder_list,
        )
        for shareholder in shareholders:
            initial_data.append({
                'contact': shareholder.contact,
                'share': shareholder.share,
                'amount': shareholder.amount,
                'option': shareholder.option,
            })
            if shareholder.option:
                self.cleaned_data['shares'] -= shareholder.amount
            else:
                self.cleaned_data['options'] -= shareholder.amount
        if self.cleaned_data['options']<0 or self.cleaned_data['shares']<0:
            return None
        shareholder_list = ShareholderList(
            company = self.cleaned_data['company'],
            date = date,
        )
        ordinary, _ = ShareType.objects.get_or_create(type='ORDINARY')
        share, _ = Share.objects.get_or_create(company=self.cleaned_data['company'], type=ordinary)
        default_contact = Contact.objects.get(pk=1) # "No Name" contact

        # Option (false)
        if self.cleaned_data['options']:
            switch = False
            for record in initial_data:
                if (record['contact'] == default_contact and
                    record['share'] == share and
                    record['option'] == False
                ):
                    switch = True
                    record['amount'] += self.cleaned_data['options']
                    break
            if not switch:
                initial_data.append({
                    'contact': default_contact,
                    'share': share,
                    'amount': self.cleaned_data['options'],
                    'option': False,
                })

        # Option (true)
        if self.cleaned_data['shares']:
            switch = False
            for record in initial_data:
                if (record['contact'] == default_contact and
                    record['share'] == share and
                    record['option'] == True
                ):
                    switch = True
                    record['amount'] += self.cleaned_data['shares']
                    break
            if not switch:
                initial_data.append({
                    'contact': default_contact,
                    'share': share,
                    'amount': self.cleaned_data['shares'],
                    'option': True,
                })
        res = []
        for record in initial_data:
            res.append(Shareholder(
                shareholder_list=shareholder_list,
                **record,
            ))
        return res
        
SharesControlFormSet = formset_factory(SharesControlForm, extra=0)

class FairValueControlForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=True,
        empty_label=None,
    )
    prev_percent=forms.ModelChoiceField(
        queryset=Percent.objects.all(),
        required=False,
        label='Prev Fair Value Method'
    )
    prev_color=forms.ChoiceField(
        choices=[('', '---------')]+COLOR_CHOICES,
        required=False,
    )
    percent = forms.ModelChoiceField(
        queryset=Percent.objects.all(),
        required=True,
        empty_label=None,
        label='Fair Value Method'
    )
    color = forms.ChoiceField(choices=COLOR_CHOICES, required=False)

    def save(self, fair_value_list):
        return FairValueMethod.objects.create(
            company=self.cleaned_data['company'],
            percent = self.cleaned_data['percent'],
            fair_value_list=fair_value_list,
            color=self.cleaned_data['color']
        )

FairValueControlFormSet = formset_factory(FairValueControlForm, extra=0)