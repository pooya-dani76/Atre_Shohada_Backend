from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.MartyrView.as_view(), name='martyr-detail'),
    path('all/', views.MartyrListView.as_view(), name='martyr-list')
]