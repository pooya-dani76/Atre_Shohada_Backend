from .models import Website
from utils.response_schema import BaseResponseSerializer
from rest_framework.serializers import ModelSerializer

class WebsiteSerializer(ModelSerializer):
    '''Serializer for the Website model, excluding the 'published' field and making 'id', 'created_at', and 'updated_at' read-only'''
    
    class Meta:
        model = Website
        exclude = ['is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
        

class WebsiteResponseSerializer(BaseResponseSerializer):
    data = WebsiteSerializer(many=True)        
         