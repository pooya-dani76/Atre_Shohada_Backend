from django.contrib import admin
from .models import ContactUs


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "subject",
        "seen"
    ]
    list_filter = ['seen']
    ordering = ['-created_at']
    readonly_fields = ("name", "email", "subject", "message", "seen", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj and not obj.seen:
            obj.seen = True
            obj.save(update_fields=["seen"])
        return obj