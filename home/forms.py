from django import forms

from .models import (
    OurTransaction, SeedStep, Share, Shareholder, SharePrice
)

class OurTransactionForm(forms.ModelForm):
    class Meta:
        model = OurTransaction
        widgets = {'date':forms.widgets.NumberInput(attrs={'type':'date'})}
        exclude = ['add_by', 'last_edit_by']


class SeedStepForm(forms.ModelForm):
    class Meta:
        model = SeedStep
        widgets = {
            'start_term':forms.widgets.NumberInput(attrs={'type':'date'}),
            'end_term':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'


class ShareForm(forms.ModelForm):
    class Meta:
        model = Share
        exclude = ['add_by']


class ShareholderForm(forms.ModelForm):
    class Meta:
        model = Shareholder
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        exclude = ['add_by', 'last_edit_by']

class SharePriceForm(forms.ModelForm):
    class Meta:
        model = SharePrice
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'