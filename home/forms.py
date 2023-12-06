from django import forms
from django.contrib import admin

from .models import OurTransaction


class DateInput(forms.DateInput):
    input_type = 'date'


class OurTransactionForm(forms.ModelForm):
    class Meta:
        model = OurTransaction
        widgets = {'date':DateInput()}
        fields = "__all__"
