from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


from core.functions import is_ajax
from core.mixins import PaginationMixin, ModelMixin, SuccessUrlMixin,FormMixin,QueryListMixin, AjaxDeleteMixin


from .models import Gallery, Media, GalleryMedia
from .forms import GalleryForm


class BaseListView(PaginationMixin,QueryListMixin,ModelMixin, LoginRequiredMixin, ListView):
    def dispatch(self, *args, **kwargs):
        self.ajax_list_partial = '{}/partials/{}_list_partial.html'.format(self.model._meta.app_label,self.model.__name__.lower())
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if is_ajax(request):
            html_form = render_to_string(
                self.ajax_list_partial, context, request)
            return JsonResponse(html_form, safe=False)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset




class GalleryList(BaseListView):
    model = Gallery
    queryset = Gallery.objects.select_related('profile').prefetch_related('gallerymedia')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset


class GalleryDetail(DetailView):
    model = Gallery
    queryset = Gallery.objects.select_related('profile').prefetch_related('gallerymedia')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_images = [media.pk for media in self.get_object().media.all()]
        images = Media.objects.exclude(
                pk__in=media_images)
        print(images.count())
        context['uploaded'] = images.count()
        return context


class GalleryCreate(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, CreateView):
    model = Gallery
    form_class = GalleryForm

    def form_valid(self,form):
        form.instance.profile = self.request.user.profile
        form.save()
        media = self.request.FILES.getlist('media')
        if media:
            for m in media:
                m_created = Media.objects.create(image=m)
                form.instance.media.add(m_created)
        return super().form_valid(form)


class GalleryUpdate(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, UpdateView):
    model = Gallery
    form_class = GalleryForm
    success_url = reverse_lazy('galleries:gallery-list')

    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset

    def form_valid(self,form):
        form.save()
        media = self.request.FILES.getlist('media')
        if media:
            for m in media:
                m_created = Media.objects.create(image=m)
                form.instance.media.add(m_created)
        return super().form_valid(form)


class GalleryDelete(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,AjaxDeleteMixin,DeleteView):
    model = Gallery
    ajax_partial = 'partials/ajax_delete_modal.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset


