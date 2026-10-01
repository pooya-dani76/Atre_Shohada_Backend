from rest_framework.serializers import ModelSerializer
from utils.response_schema import BaseResponseSerializer
from .models import ContactUs

class ContactUsSerializer(ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'name', 'email', 'subject', 'message', 'seen', 'created_at']
        read_only_fields = ['id', 'created_at', 'seen']
        

class ContactUsResponseSerializer(BaseResponseSerializer):
    data = ContactUsSerializer()