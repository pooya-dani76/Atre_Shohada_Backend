from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from utils.response_schema import pagination_parameters, ErrorResponseSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .serializers import BlogResponseSerializer, BlogListSerializer
from .models import Blog
from .paginations import BlogPagination
from django.db.models import Q


class BlogDetailView(APIView):
    @extend_schema(
        operation_id='Get Blog',
        responses={
            200: BlogResponseSerializer,
            404: ErrorResponseSerializer,
            403: ErrorResponseSerializer
        },
        parameters=[
            OpenApiParameter(name='X-Api-Key', location=OpenApiParameter.HEADER, required=True, type=str),
        ],
        tags=["Blog"]
    )
    def get(self, request: Request, pk: int | None = None, slug: str | None = None) -> Response:
        if pk:
            blog = get_object_or_404(Blog, pk=pk, is_published=True) 
        if slug:
            blog = get_object_or_404(Blog, slug=slug, is_published=True) 
        response_serializer =  BlogResponseSerializer({"message": "Blog Data Retrieved Successfully", "data": blog}, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    

class BlogSearchView(APIView):

    @extend_schema(
        operation_id='List Blogs',
        responses={
            200: BlogPagination.get_paginated_response_serializer(serializer=BlogListSerializer),
            403: ErrorResponseSerializer
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
        blogs = Blog.objects.filter(is_published=True)
        if search:
            blogs = blogs.filter(Q(title__icontains=search) | Q(summary__icontains=search) | Q(content__icontains=search))
        paginator = BlogPagination()
        paginated_blogs = paginator.paginate_queryset(blogs, request)
        serializer = BlogListSerializer(paginated_blogs, many=True)
        return paginator.get_paginated_response(serializer.data)