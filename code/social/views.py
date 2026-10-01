from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import SocialInfoResponseSerializer
from .models import SocialInfo   
from utils.response_schema import BaseErrorResponseSerializer



class SocialInfoView(APIView):
    @extend_schema(
        summary="Retrieve List of Social Info",
        description="This endpoint retrieves a list of all Social Info",
        responses={
            403: BaseErrorResponseSerializer,
            200: SocialInfoResponseSerializer,
        },
    )
    def get(self, request: Request):
        social_infos = SocialInfo.objects.filter(active=True)
        serializer = SocialInfoResponseSerializer({"message": "Social Info Retrieved Successfully", "data": social_infos}, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)