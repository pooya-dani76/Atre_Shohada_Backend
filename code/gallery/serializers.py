from utils.response_schema import BaseSafeImageSerializer
from .models import Gallery

class GallerySerializer(BaseSafeImageSerializer):
    '''Serializer for the Gallery model, excluding the 'is_active' field and making 'id', 'created_at', and 'updated_at' read-only'''
    class Meta:
        model = Gallery
        fields = ['martyr', 'description', 'image']