from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.SliderListView.as_view(), name='slider-list')
]