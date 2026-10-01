from django.apps import AppConfig


class MartyrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'martyr'
    
    def ready(self):
        from . import receivers  
