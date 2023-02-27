import os
import hashlib
import datetime
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.html import format_html, mark_safe
# Create your models here.

from core.models import Timestamped
from core.storage import OverwriteStorage
from profiles.models import Profile


def _delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)


def get_upload_path(instance, filename):
    name = instance.__class__.__name__.lower()
    return os.path.join('{}_{}_{}/{}/{}'.format(
        datetime.datetime.now().day,
        datetime.datetime.now().month,
        datetime.datetime.now().year, name, filename))



class Media(Timestamped):
    image = models.ImageField(upload_to=get_upload_path,
                              storage=OverwriteStorage())
    class Meta:
        default_related_name = 'media'
        verbose_name = 'media'
        verbose_name_plural = 'media'

    
    def __str__(self):
        return os.path.basename(self.image.name)

    def get_thumb(self):
        if self.image:
            return format_html("<img src='{}' width='100' height='auto'>",
                               self.image.url)
        return ''


class Gallery(Timestamped):
    name = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    media = models.ManyToManyField(Media, through='GalleryMedia', related_name='gallery_media')

    class Meta:
        default_related_name = 'galleries'
        verbose_name = 'gallery'
        verbose_name_plural = 'galleries'

    def __str__(self):
        return self.name


class GalleryMedia(Timestamped):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'gallerymedia'
        verbose_name = 'gallery media'
        verbose_name_plural = 'gallery media'

    def __str__(self):
        return self.gallery.name

    def get_thumb(self):
        if self.media:
            return format_html("<img src='{}' width='100' height='auto'>",
                               self.media.url)
        return ''


@receiver(models.signals.pre_delete, sender=Media)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    exists = GalleryMedia.objects.filter(media=instance)
    counter = exists.count()
    if instance.image:
        if counter == 1:
            _delete_file(instance.image.path)
