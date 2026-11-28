from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import WebsiteResponseSerializer
from .models import Website   
from utils.response_schema import ErrorResponseSerializer
from utils.response_schema import api_key_parameter



class WebsiteListView(APIView):
    @extend_schema(
        summary="Retrieve List of Websites",
        description="This endpoint retrieves a list of all Websites",
        responses={
            403: ErrorResponseSerializer,
            200: WebsiteResponseSerializer,
        },
        parameters=[api_key_parameter],
        tags=["Websites"]
    )
    def get(self, request: Request):
        websites = Website.objects.filter(is_published=True)
        serializer = WebsiteResponseSerializer({"message": "Websites Retrieved Successfully", "data": websites}, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)