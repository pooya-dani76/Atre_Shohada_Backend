from .models import Slider
from utils.response_schema import BaseSafeImageSerializer, BaseResponseSerializer

class SliderSerializer(BaseSafeImageSerializer):
    '''Serializer for the Slider model, excluding the 'published' field and making 'id', 'created_at', and 'updated_at' read-only'''
    
    class Meta:
        model = Slider
        exclude = ['published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
        

class SliderResponseSerializer(BaseResponseSerializer):
    data = SliderSerializer(many=True)        
         