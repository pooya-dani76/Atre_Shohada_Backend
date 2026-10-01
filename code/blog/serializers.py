from .models import Blog
from utils.response_schema import BaseSafeImageSerializer


class BlogSerializer(BaseSafeImageSerializer):

    class Meta:
        model = Blog
        exclude = ['published', 'created_at', 'updated_at']
        read_only_fields = ['id', ]