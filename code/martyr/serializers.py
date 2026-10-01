from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import Martyr
from gallery.serializers import GallerySerializer
from utils.response_schema import BaseSafeImageSerializer, BaseResponseSerializer
from drf_spectacular.utils import extend_schema_field



class MartyrSerializer(BaseSafeImageSerializer):
    '''Serializer for the Martyr model, excluding the 'is_active' field and making 'id', 'created_at', and 'updated_at' read-only'''
    all_images = SerializerMethodField()
    
    
    @extend_schema_field(GallerySerializer(many=True))
    def get_all_images(self, obj):
        '''Retrieve all associated images for the Martyr instance'''
        active_images = obj.gallery.filter(is_active=True)
        return GallerySerializer(active_images, many=True).data
    
    
    dispatch_type = CharField(source='get_dispatch_type_display', read_only=True)

    graduation = CharField(source='get_graduation_display', read_only=True)

    marriage_status = CharField(source='get_marriage_status_display', read_only=True)
    
    class Meta:
        model = Martyr
        exclude = ['is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        


class MartyrListSerializer(ModelSerializer):
    '''Serializer for listing Martyr instances, including only 'id', 'first_name', 'last_name', and 'image' fields'''
    
    class Meta:
        model = Martyr
        fields = ['id', 'first_name', 'last_name', 'cover_image']  
        
        
class MartyrResponseSerializer(BaseResponseSerializer):
    data = MartyrSerializer()          