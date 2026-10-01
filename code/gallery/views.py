from rest_framework.views import APIView
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from .serializers import GallerySerializer
from.models import Gallery   
from .paginations import GalleryPagination
from utils.response_schema import BaseErrorResponseSerializer
from .schema import  martyr_search_parameter



class GalleryListView(APIView):
    @extend_schema(
        summary="Retrieve List of Martyr Images",
        description="This endpoint retrieves a list of all Martyr Images",
        responses={
            403: BaseErrorResponseSerializer,
            200: GalleryPagination.get_paginated_response_serializer(serializer=GallerySerializer),
        },
        parameters=[
            martyr_search_parameter
        ]
    )
    def get(self, request: Request):
        martyr = request.query_params.get('martyr', None)
        
        gallery_items = Gallery.objects.filter(is_active=True)
        
        if martyr:
            gallery_items = gallery_items.filter(martyr__id=martyr, martyr__is_active=True)
            
        paginator = GalleryPagination()
        paginated_gallery_items = paginator.paginate_queryset(gallery_items, request)
        
        serializer = GallerySerializer(paginated_gallery_items, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)    