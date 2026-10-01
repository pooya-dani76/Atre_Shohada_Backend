from django.contrib import admin
from .models import Martyr
from gallery.models import Gallery
from django.utils.html import format_html
from django import forms
from django_jalali.admin.widgets import AdminjDateWidget


class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1
    show_change_link = True
    fields = ['image', 'image_preview', 'description', 'is_active']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                f'<a href="{obj.image.url}" target="_blank">'
                f'<img src="{obj.image.url}" style="max-height: 80px; max-width: 80px;" />'
                f'</a>'
            )
        return "No Image"

    image_preview.short_description = "image preview"
    
    
class MartyrAdminForm(forms.ModelForm):
    class Meta:
        model = Martyr
        fields = '__all__'
        widgets = {
            'martyrdom_date': AdminjDateWidget,
        }


@admin.register(Martyr)
class MartyrAdmin(admin.ModelAdmin):
    form = MartyrAdminForm
    inlines = [GalleryInline]
    search_fields = ['name']
    list_per_page = 25
    list_display = [
        "full_name",
        "is_active",
    ]
    ordering = ['-created_at']
    readonly_fields = ("created_at","updated_at")
    list_editable= ("is_active",)
    
    @admin.display(description="نام و نام خانوادگی")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"