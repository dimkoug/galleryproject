from django import forms
from core.forms import BootstrapForm

from .models import Gallery


class GalleryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ('name',)


