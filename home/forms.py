from django import forms

from .models import OurTransaction, Company

class OurTransactionForm(forms.ModelForm):
    class Meta:
        model = OurTransaction
        widgets = {'date':forms.widgets.NumberInput(attrs={'type':'date'})}
        fields = "__all__"

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"