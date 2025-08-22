from django import forms

class StandardUploadForm(forms.Form):
    file = forms.FileField()