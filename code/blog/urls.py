from django.urls import path
from . import views

urlpatterns = [
    path("all/", views.BlogSearchView.as_view(), name="blog-search"),
    path("<int:pk>/", views.BlogDetailView.as_view(), name="blog-detail")
]
