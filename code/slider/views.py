from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import SliderResponseSerializer
from .models import Slider   
from utils.response_schema import BaseErrorResponseSerializer



class SliderListView(APIView):
    @extend_schema(
        summary="Retrieve List of Sliders",
        description="This endpoint retrieves a list of all Sliders",
        responses={
            403: BaseErrorResponseSerializer,
            200: SliderResponseSerializer,
        },
    )
    def get(self, request: Request):
        sliders = Slider.objects.filter(published=True)
        serializer = SliderResponseSerializer({"message": "Sliders Retrieved Successfully", "data": sliders}, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)