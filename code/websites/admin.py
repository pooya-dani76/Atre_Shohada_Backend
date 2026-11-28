from django.contrib import admin
from .models import Website


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_per_page = 25
    list_display = [
        "title",
        "order",
        "is_published",
    ]
    ordering = ['-created_at']
    readonly_fields = ("created_at","updated_at",)
    list_editable= ("is_published", "order")
