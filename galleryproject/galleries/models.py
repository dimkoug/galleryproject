import os
import hashlib
import datetime
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.html import format_html, mark_safe
# Create your models here.


def _delete_file(path):
    """ Deletes file from filesystem. """
    print(path)
    if os.path.isfile(path):
        os.remove(path)


class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise(Exception("name's length is greater than max_length"))
        return name

    def _save(self, name, content):
        if self.exists(name):
            # if the file exists, do not call the superclasses _save method
            return name
        # if the file is new, DO call it
        return super(MediaFileSystemStorage, self)._save(name, content)


class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_upload_path(instance, filename):
    name = instance.__class__.__name__.lower()
    return os.path.join('{}_{}_{}/{}/{}'.format(
        datetime.datetime.now().day,
        datetime.datetime.now().month,
        datetime.datetime.now().year, name, filename))


class Media(Timestamped):
    image = models.ImageField(upload_to=get_upload_path,
                              storage=MediaFileSystemStorage())
    caption = models.CharField(blank=True, max_length=100)
    name = models.CharField(blank=True, max_length=255)
    md5sum = models.CharField(blank=True, max_length=255)

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

    def save(self, *args, **kwargs):
        if not self.pk:  # file is new
            md5 = hashlib.md5()
            for chunk in self.image.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        super(Media, self).save(*args, **kwargs)


class Gallery(Timestamped):
    name = models.CharField(max_length=100)
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
