from django.urls import reverse_lazy

class SuccessMixin:
    def get_success_url(self):
        app = self.model._meta.app_label
        model_name = self.model.__name__.lower()
        url_path = "{}:{}-list".format(app, model_name)
        url = reverse_lazy(url_path)
        if 'gallery' in self.request.GET:
            gallery_id = self.request.GET.get('gallery')
            url = reverse_lazy('{}:{}-detail'.format(app, 'gallery'),
                               kwargs={'pk': gallery_id})
        return url
