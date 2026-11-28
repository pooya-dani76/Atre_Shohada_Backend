from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import SliderResponseSerializer
from .models import Slider   
from utils.response_schema import ErrorResponseSerializer
from utils.response_schema import api_key_parameter



class SliderListView(APIView):
    @extend_schema(
        summary="Retrieve List of Sliders",
        description="This endpoint retrieves a list of all Sliders",
        responses={
            403: ErrorResponseSerializer,
            200: SliderResponseSerializer,
        },
        parameters=[api_key_parameter],
        tags=["Slider Images"]
    )
    def get(self, request: Request):
        sliders = Slider.objects.filter(is_published=True)
        serializer = SliderResponseSerializer({"message": "Sliders Retrieved Successfully", "data": sliders}, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)