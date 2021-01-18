from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CKUploadImage


CLASSES = 'input is-primary is-rounded'


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(
            attrs={'class': CLASSES, 'placeholder': _('Username')}
        )
    )
    password = forms.CharField(
        max_length=100, widget=forms.PasswordInput(
            attrs={'class': CLASSES, 'placeholder': _('Password')}
        )
    )


class NewFolderForm(forms.Form):
    name = forms.CharField(max_length=50)
    public = forms.BooleanField(required=False)


class NewFileForm(forms.Form):
    name = forms.CharField(max_length=100)
    content = forms.FileField()


class CKUploadImageForm(forms.ModelForm):
    class Meta:
        model = CKUploadImage
        fields = ['upload']


class EditorForm(forms.Form):
    editor = forms.CharField()
    name = forms.CharField()
