from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .serializers import MartyrListSerializer, MartyrResponseSerializer
from .models import Martyr, MarriageStatus
from .paginations import MartyrPagination
from utils.response_schema import ErrorResponseSerializer
from django.db.models import Q
from .schema import martyr_list_parameters
from utils.response_schema import api_key_parameter


class MartyrView(APIView):
    @extend_schema(
        summary="Retrieve Martyr Data",
        description="This endpoint retrieves data related to Martyr",
        responses={
            200: MartyrResponseSerializer,
            404: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        parameters=[api_key_parameter],
        tags=["Martyr"]
    )
    def get(self, request: Request, id: int):
        martyr = get_object_or_404(Martyr, id=id, is_published=True)
        response_serializer =  MartyrResponseSerializer({"message": "Martyr Data Retrieved Successfully", "data": martyr}, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    
class MartyrListView(APIView):
    @extend_schema(
        summary="Retrieve List of Martyrs",
        description="This endpoint retrieves a list of all Martyrs",
        responses={
            403: ErrorResponseSerializer,
            200: MartyrPagination.get_paginated_response_serializer(serializer=MartyrListSerializer),
        },
        parameters=martyr_list_parameters + [api_key_parameter],
        tags=["Martyr"]
    )
    def get(self, request: Request):
        name = request.query_params.get('name', None)
        dispatch = request.query_params.get('dispatch', None)
        martyrdom = request.query_params.get('martyrdom', None)
        graduation = request.query_params.get('graduation', None)
        married = request.query_params.get('married', None)
        category = request.query_params.get('category', None)
        
        if married is not None:
            if married.lower() == 'true':
                married = True
            elif married.lower() == 'false':
                married = False
            else:
                married = None    
        martyrs = Martyr.objects.filter(is_published=True)
        if name:
            martyrs = martyrs.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
            
        if married is not None:
            if married:
                martyrs = martyrs.filter(marriage_status=MarriageStatus.MARRIED)
            else:
                martyrs = martyrs.filter(marriage_status=MarriageStatus.SINGLE)
            
        if dispatch:
            martyrs = martyrs.filter(dispatch_type=dispatch)
            
        if martyrdom:
            martyrs = martyrs.filter(martyrdom_location__icontains=martyrdom)
            
        if graduation:
            martyrs = martyrs.filter(graduation=graduation)
        
        if category:
            martyrs = martyrs.filter(category=category)
            
        paginator = MartyrPagination()
        paginated_martyrs = paginator.paginate_queryset(martyrs, request)
        
        serializer = MartyrListSerializer(paginated_martyrs, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)       