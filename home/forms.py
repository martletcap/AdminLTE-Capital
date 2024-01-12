from django import forms
from django.contrib.auth import get_user_model

from .models import (
    Company, SeedStep, Split, Shareholder, SharePrice, MoneyTransaction,
    ShareTransaction, FairValueMethod,
)
from .utils import UserChoiceField

User = get_user_model()


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


class SplitForm(forms.ModelForm):
    class Meta:
        model = Split
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
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


class MoneyTransactionForm(forms.ModelForm):

    class Meta:
        model = MoneyTransaction
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'


class ShareTransactionForm(forms.ModelForm):
    class Meta:
        model = ShareTransaction
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'


class FairValueMethodForm(forms.ModelForm):
    percent = forms.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = FairValueMethod
        widgets = {
            'date':forms.widgets.NumberInput(attrs={'type':'date'}),
        }
        fields = '__all__'