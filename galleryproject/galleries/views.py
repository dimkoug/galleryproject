from django.shortcuts import render
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Gallery, Media, GalleryMedia
from .forms import GalleryForm, MediaForm
from .mixins import SuccessMixin


class GalleryList(ListView):
    model = Gallery
    queryset = Gallery.objects.prefetch_related('gallerymedia')


class GalleryDetail(DetailView):
    model = Gallery
    queryset = Gallery.objects.prefetch_related('gallerymedia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_images = [media.pk for media in self.get_object().media.all()]
        images = Media.objects.exclude(
                pk__in=media_images)
        print(images.count())
        context['uploaded'] = images.count()
        return context


class GalleryCreate(CreateView):
    model = Gallery
    form_class = GalleryForm
    success_url = reverse_lazy('galleries:gallery-list')

    def form_valid(self, form):
        form.save()
        message_text = 'Your {} was created successfully!'.format(form.instance)
        messages.success(self.request, message_text)
        if 'continue' in self.request.POST:
            return HttpResponseRedirect(
                    reverse_lazy('galleries:gallery-update',
                                 kwargs={'pk': form.instance.pk}))
        else:
            return super().form_valid(form)


class GalleryUpdate(UpdateView):
    model = Gallery
    form_class = GalleryForm
    success_url = reverse_lazy('galleries:gallery-list')

    def form_valid(self, form):
        form.save()
        message_text = 'Your {} was updated successfully!'.format(form.instance)
        messages.success(self.request, message_text)
        if 'continue' in self.request.POST:
            return HttpResponseRedirect(reverse_lazy(
                'galleries:gallery-update', kwargs={'pk': form.instance.pk}))
        else:
            return super().form_valid(form)


class GalleryDelete(DeleteView):
    model = Gallery
    success_url = reverse_lazy('galleries:gallery-list')


class MediaList(ListView):
    model = Media
    queryset = Media.objects.prefetch_related('gallery_media')


class MediaDetail(DetailView):
    model = Media
    queryset = Media.objects.prefetch_related('gallery_media')


class MediaCreate(SuccessMixin, CreateView):
    model = Media
    form_class = MediaForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        gallery = None
        if 'gallery' in self.request.GET:
            gallery = Gallery.objects.get(pk=self.request.GET.get('gallery'))
        message_text = 'Your {} was created successfully!'.format(form.instance)
        messages.success(self.request, message_text)
        if self.request.FILES['image']:
            for f in self.request.FILES.getlist('image'):
                print(f.name)
                try:
                    obj = Media.objects.get(name=f.name)
                except Media.DoesNotExist:
                    obj.pk = None
                    obj.name = f.name
                    obj.image = f
                    obj.save()
                if gallery:
                    gallery.media.add(obj)

        if 'continue' in self.request.POST:
            return HttpResponseRedirect(
                    reverse_lazy('galleries:media-update',
                                 kwargs={'pk': form.instance.pk}))
        else:
            return super().form_valid(form)


class MediaUpdate(SuccessMixin, UpdateView):
    model = Media
    form_class = MediaForm

    def form_valid(self, form):
        form.save()
        message_text = 'Your {} was updated successfully!'.format(form.instance)
        messages.success(self.request, message_text)
        if 'continue' in self.request.POST:
            return HttpResponseRedirect(reverse_lazy(
                'galleries:media-update', kwargs={'pk': form.instance.pk}))
        else:
            return super().form_valid(form)


class MediaDelete(SuccessMixin, DeleteView):
    model = Media

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'gallery' in self.request.GET:
            gallery = Gallery.objects.get(pk=self.request.GET.get('gallery'))
            gallery.media.remove(self.object)
        exists = ''
        media = GalleryMedia.objects.filter(media=self.object)
        if not media:
            self.object.delete()
        else:
            message_text = 'Your {} is used in some galleries'.format(self.object)
            messages.error(self.request, message_text)
        return HttpResponseRedirect(super().get_success_url())


def uploaded_image(request, pk):
    context = {}
    template = 'galleries/uploaded.html'
    gallery = get_object_or_404(Gallery, pk=pk)
    context['gallery'] = gallery
    media_images = [media.pk for media in gallery.media.all()]
    images = Media.objects.exclude(
            pk__in=media_images)
    if request.method == 'POST':
        for pk in request.POST.getlist('image[]'):
            image = Media.objects.get(pk=pk)
            gallery.media.add(image)
            media_images = [media.pk for media in gallery.media.all()]
            images = Media.objects.exclude(
                pk__in=media_images)
        return HttpResponseRedirect(reverse_lazy(
                'galleries:gallery-detail', kwargs={'pk': gallery.pk}))
    context['images'] = images
    return render(request, template, context)
