from django import forms

from .models import OurTransaction

class OurTransactionForm(forms.ModelForm):
    class Meta:
        model = OurTransaction
        widgets = {'date':forms.widgets.NumberInput(attrs={'type':'date'})}
        fields = "__all__"
