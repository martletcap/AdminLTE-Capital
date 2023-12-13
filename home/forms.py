from django import forms
from django.contrib.auth import get_user_model

from .models import (
    OurTransaction, Company, SeedStep, Share, Shareholder, SharePrice
)
from .utils import UserChoiceField

User = get_user_model()


class OurTransactionForm(forms.ModelForm):
    save_price = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = OurTransaction
        widgets = {'date':forms.widgets.NumberInput(attrs={'type':'date'})}
        fields = [
            'share', 'date', 'amount', 'price', 'save_price', 'comment',
        ]


class CompanyForm(forms.ModelForm):
    staff = UserChoiceField(queryset=User.objects.all())
    class Meta:
        model = Company
        fields = '__all__'

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