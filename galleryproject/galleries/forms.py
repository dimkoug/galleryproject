from django import forms
from .models import Gallery, Media


class BootstrapForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = ['CheckboxInput', 'ClearableFileInput', 'FileInput']
        for field in self.fields:
            widget_name = self.fields[field].widget.__class__.__name__
            if widget_name not in fields:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })


class GalleryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ('name',)


class MediaForm(BootstrapForm, forms.ModelForm):
    image = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Media
        fields = ('image', 'caption')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['image'].widget.attrs['multiple'] = False
        else:
            self.fields.pop('caption')
