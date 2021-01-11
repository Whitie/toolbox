from django import forms
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=150)
    password = forms.CharField(label=_('Password'), max_length=100,
                               widget=forms.PasswordInput)


class NewFolderForm(forms.Form):
    name = forms.CharField(max_length=50)
    public = forms.BooleanField(required=False)


class NewFileForm(forms.Form):
    name = forms.CharField(max_length=100)
    content = forms.FileField()
