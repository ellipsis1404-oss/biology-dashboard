from django import forms

class StandardUploadForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'accept': '.xlsx, .csv'}))