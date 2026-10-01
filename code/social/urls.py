from django.urls import path
from .views import SocialInfoView

urlpatterns = [
    path('', SocialInfoView.as_view(), name='social-info')
]