from django.urls import path

from .views import (
    GalleryList,
    GalleryDetail,
    GalleryCreate,
    GalleryUpdate,
    GalleryDelete,
    MediaList,
    MediaDetail,
    MediaCreate,
    MediaUpdate,
    MediaDelete,
    uploaded_image,
)

app_name = 'galleries'
urlpatterns = [
    path('', GalleryList.as_view(), name='gallery-list'),
    path('<int:pk>/detail/', GalleryDetail.as_view(), name='gallery-detail'),
    path('create/', GalleryCreate.as_view(), name='gallery-create'),
    path('<int:pk>/update/', GalleryUpdate.as_view(), name='gallery-update'),
    path('<int:pk>/delete/', GalleryDelete.as_view(), name='gallery-delete'),

    path('media/', MediaList.as_view(), name='media-list'),
    path('media/<int:pk>/detail/', MediaDetail.as_view(), name='media-detail'),
    path('media/create/', MediaCreate.as_view(), name='media-create'),
    path('media/<int:pk>/update/', MediaUpdate.as_view(), name='media-update'),
    path('media/<int:pk>/delete/', MediaDelete.as_view(), name='media-delete'),
    path('media/<int:pk>/uploaded/', uploaded_image, name='uploaded-images'),
]
