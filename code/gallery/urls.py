from django.urls import path
from .views import GalleryListView

urlpatterns = [
    path('all/', GalleryListView.as_view(), name='gallery-list'),
]