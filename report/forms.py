import datetime
from typing import Any

from django import forms
from django.forms import formset_factory

from home.models import Share, ShareType, ContactType, Contact, Company
from home.forms import SharePriceForm

class UploadFileForm(forms.Form):
    file = forms.FileField()

# class ShareholderExtraForm(forms.Form):
#     company = forms.ModelChoiceField(
#         queryset=Company.objects.all(),
#         widget=forms.HiddenInput(),
#     )
#     date = forms.DateField(widget=forms.widgets.NumberInput(attrs={'type':'date'}))

        

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


SharePriceFormSet = formset_factory(SharePriceUpdateForm, extra=0)