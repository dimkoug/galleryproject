from django.urls import path

from .views import (
    GalleryList,
    GalleryDetail,
    GalleryCreate,
    GalleryUpdate,
    GalleryDelete,
)

app_name = 'galleries'
urlpatterns = [
    path('', GalleryList.as_view(), name='gallery-list'),
    path('<int:pk>/detail/', GalleryDetail.as_view(), name='gallery-detail'),
    path('create/', GalleryCreate.as_view(), name='gallery-create'),
    path('<int:pk>/update/', GalleryUpdate.as_view(), name='gallery-update'),
    path('<int:pk>/delete/', GalleryDelete.as_view(), name='gallery-delete'),
]
