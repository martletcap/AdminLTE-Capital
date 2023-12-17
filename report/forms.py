from django import forms

from home.models import Shareholder


class UploadFileForm(forms.Form):
    file = forms.FileField()


class ShareholderUploadForm(forms.Form):
    name = forms.CharField()
    company = forms.CharField()
    type = forms.CharField()
    amount = forms.IntegerField()
