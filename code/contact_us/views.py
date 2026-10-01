from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from utils.response_schema import BaseErrorResponseSerializer
from drf_spectacular.utils import extend_schema
from .serializers import ContactUsSerializer, ContactUsResponseSerializer


class ContactUsView(APIView):
    @extend_schema(
        summary="Create a new contact us message",
        description="This endpoint allows users to submit a new contact us message.",
        request=ContactUsSerializer,
        responses={
            201: ContactUsResponseSerializer,
            400: BaseErrorResponseSerializer,
            403: BaseErrorResponseSerializer
        },
    )
    def post(self, request: Request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ContactUsResponseSerializer({
                "message": "Your Message Submited Successfully",
                "data": serializer.data
            })
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        error_serializer = BaseErrorResponseSerializer({"message": serializer.errors})
        return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)