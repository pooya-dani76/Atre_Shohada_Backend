from django.contrib import admin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
        'published',
    ]
    list_filter = ['title', 'published']
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at', 'slug')

    fields = (
        'title', 'content', 'summary',
        'image', 'image_alt', 'meta_title', 'meta_description',
        'published', 'slug', 'created_at', 'updated_at',
    )