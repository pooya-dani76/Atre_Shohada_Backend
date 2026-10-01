from django.apps import AppConfig


class SliderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'slider'
    
    def ready(self):
        from . import receivers  
