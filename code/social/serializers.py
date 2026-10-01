from .models import SocialInfo
from rest_framework.serializers import ModelSerializer 
from utils.response_schema import BaseResponseSerializer

class SocialInfoSerializer(ModelSerializer):
    '''Serializer for the SocialInfo model, excluding the 'active' field and making 'id', 'created_at', and 'updated_at' read-only'''
    
    class Meta:
        model = SocialInfo
        exclude = ['active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
        

class SocialInfoResponseSerializer(BaseResponseSerializer):
    data = SocialInfoSerializer(many=True)   