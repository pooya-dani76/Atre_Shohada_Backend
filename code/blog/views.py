from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from utils.swagger_schema import pagination_parameters, error_404, error_403
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .serializers import BlogSerializer
from .models import Blog
from .paginations import BlogPagination
from utils.swagger_schema import get_paginated_response
from django.db.models import Q


class BlogDetailView(APIView):
    @extend_schema(
        operation_id='Get Blog',
        responses={
            200: BlogSerializer,
            404: error_404,
            403: error_403
        },
        parameters=[
            OpenApiParameter(name='X-Api-Key', location=OpenApiParameter.HEADER, required=True, type=str),
        ],
        tags=["Blog"]
    )
    def get(self, request: Request, pk: int) -> Response:
        blog = get_object_or_404(Blog, pk=pk, published=True)
        return Response(BlogSerializer(blog).data, status=status.HTTP_200_OK)
    
    

class BlogSearchView(APIView):

    @extend_schema(
        operation_id='List Blogs',
        responses={
            200: get_paginated_response(BlogSerializer),
            403: error_403
        },
        parameters=[
            *pagination_parameters,
            OpenApiParameter(name='X-Api-Key', location=OpenApiParameter.HEADER, required=True, type=str),
            OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Search blogs by its content, title and summary", required=False)
        ],
        tags=["Blog"]
    )
    def get(self, request: Request) -> Response:
        search = request.query_params.get("search")
        blogs = Blog.objects.filter(published=True)
        if search:
            blogs = blogs.filter(Q(title__icontains=search) | Q(summary__icontains=search) | Q(content__icontains=search))
        paginator = BlogPagination()
        paginated_blogs = paginator.paginate_queryset(blogs, request)
        serializer = BlogSerializer(paginated_blogs, many=True)
        return paginator.get_paginated_response(serializer.data)