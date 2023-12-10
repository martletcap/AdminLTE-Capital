from django import forms

from .models import OurTransaction, Company, SeedStep, Shareholder, SharePrice

class OurTransactionForm(forms.ModelForm):
    class Meta:
        model = OurTransaction
        widgets = {'date':forms.widgets.NumberInput(attrs={'type':'date'})}
        fields = "__all__"

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"

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