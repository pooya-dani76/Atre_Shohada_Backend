"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import SecureSchemaView, SecureSwaggerView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('martyrs/', include('martyr.urls')),
    path('gallery/', include('gallery.urls')),
    path('contact-us/', include('contact_us.urls')),
    path('slider/', include('slider.urls')),
    path('social/', include('social.urls')),
    # path('blog/', include('blog.urls')),
    
    path('api/schema/', SecureSchemaView.as_view(), name='schema'),
    path('api/docs/', SecureSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)