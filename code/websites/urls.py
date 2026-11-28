from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.WebsiteListView.as_view(), name='website-list')
]