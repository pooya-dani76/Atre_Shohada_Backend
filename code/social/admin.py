from django.contrib import admin
from .models import SocialInfo


@admin.register(SocialInfo)
class SocialInfoAdmin(admin.ModelAdmin):
    list_display = ("email",)

    def has_add_permission(self, request):
        return not SocialInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False