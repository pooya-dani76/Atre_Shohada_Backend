from .models import Blog
from utils.response_schema import BaseResponseSerializer, BaseSafeImageSerializer


class BlogSerializer(BaseSafeImageSerializer):

    class Meta:
        model = Blog
        exclude = ['is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', ]
        
        
class BlogResponseSerializer(BaseResponseSerializer):
    data = BlogSerializer()     
    
    
class BlogListSerializer(BaseSafeImageSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'image']     