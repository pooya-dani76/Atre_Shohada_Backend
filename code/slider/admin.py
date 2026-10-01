from django.contrib import admin, messages
from .models import Slider, SliderSetting
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django import forms


class SliderAdminForm(forms.ModelForm):
    class Meta:
        model = Slider
        fields = "__all__"


@admin.register(SliderSetting)
class SliderSettingAdmin(admin.ModelAdmin):
    list_display = ("max_active_sliders",)

    def has_add_permission(self, request):
        return not SliderSetting.objects.exists()


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    form = SliderAdminForm
    search_fields = ['title']
    list_per_page = 25
    list_display = [
        "title",
        "image_preview",
        "published",
    ]
    ordering = ['-created_at']
    readonly_fields = ("created_at","updated_at", "image_preview")
    list_editable= ("published",)
    
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                f'<a href="{obj.image.url}" target="_blank">'
                f'<img src="{obj.image.url}" style="max-height: 80px; max-width: 80px;" />'
                f'</a>'
            )
        return "No Image"
    
    image_preview.short_description = "image preview"