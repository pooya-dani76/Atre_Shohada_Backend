from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .serializers import MartyrListSerializer, MartyrResponseSerializer
from .models import Martyr   
from .paginations import MartyrPagination
from utils.response_schema import BaseErrorResponseSerializer
from django.db.models import Q
from .schema import (
    name_search_parameter,
    biography_search_parameter,
    narrative_search_parameter,
    testament_search_parameter,
    pilgrimage_letter_search_parameter,
)


class MartyrView(APIView):
    @extend_schema(
        summary="Retrieve Martyr Data",
        description="This endpoint retrieves data related to Martyr",
        responses={
            200: MartyrResponseSerializer,
            404: BaseErrorResponseSerializer,
            403: BaseErrorResponseSerializer,
        },
    )
    def get(self, request: Request, id: int):
        martyr = get_object_or_404(Martyr, id=id, is_active=True)
        response_serializer =  MartyrResponseSerializer({"message": "Martyr Data Retrieved Successfully", "data": martyr}, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    
class MartyrListView(APIView):
    @extend_schema(
        summary="Retrieve List of Martyrs",
        description="This endpoint retrieves a list of all Martyrs",
        responses={
            403: BaseErrorResponseSerializer,
            200: MartyrPagination.get_paginated_response_serializer(serializer=MartyrListSerializer),
        },
        parameters=[
            name_search_parameter,
            biography_search_parameter,
            narrative_search_parameter,
            testament_search_parameter,
            pilgrimage_letter_search_parameter,
        ]
    )
    def get(self, request: Request):
        name = request.query_params.get('name', None)
        testament = request.query_params.get('testament', None)
        biography = request.query_params.get('biography', None)
        narrative = request.query_params.get('narrative', None)
        pilgrimage_letter = request.query_params.get('pilgrimage_letter', None)
        
        martyrs = Martyr.objects.all()
        if name:
            martyrs = martyrs.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
        if testament:
            martyrs = martyrs.filter(testament__icontains=testament)
        if biography:
            martyrs = martyrs.filter(biography__icontains=biography)
        if narrative:
            martyrs = martyrs.filter(narrative__icontains=narrative)
        if pilgrimage_letter:
            martyrs = martyrs.filter(pilgrimage_letter__icontains=pilgrimage_letter)
            
        paginator = MartyrPagination()
        paginated_martyrs = paginator.paginate_queryset(martyrs, request)
        
        serializer = MartyrListSerializer(paginated_martyrs, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)    