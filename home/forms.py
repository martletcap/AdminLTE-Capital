from django import forms
from django.contrib.auth import get_user_model

from .models import (
    OurTransaction, Company, SeedStep, Share, Shareholder, SharePrice
)
from .utils import UserChoiceField

User = get_user_model()


class OurTransactionForm(forms.ModelForm):
    save_price = forms.BooleanField(
        initial=True, required=False, label='Save history market price',
    )

    class Meta:
        model = OurTransaction
        widgets = {'date':forms.widgets.NumberInput(attrs={'type':'date'})}
        fields = '__all__'


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


class ShareholderForm(forms.ModelForm):
    class Meta:
        model = Shareholder
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'

class SharePriceForm(forms.ModelForm):
    class Meta:
        model = SharePrice
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'