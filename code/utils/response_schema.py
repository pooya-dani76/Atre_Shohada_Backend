from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_spectacular.utils import inline_serializer
import os



class BaseResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = serializers.JSONField(allow_null=True)
    


class BasePaginator(PageNumberPagination):
    page_size = 10 
    max_page_size = 100
    message = ""

    def get_paginated_response(self, data):
        return Response({
            'message': self.message,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })
    
    
    @classmethod
    def get_paginated_response_serializer(cls, serializer):
        return inline_serializer(
            name=f"{serializer.__name__}PaginatedResponse",
            fields={
                "message": serializers.CharField(),
                "count": serializers.IntegerField(),
                "next": serializers.URLField(allow_null=True),
                "previous": serializers.URLField(allow_null=True),
                "data": serializer(many=True),
            },
        )    



class BaseSafeImageSerializer(serializers.ModelSerializer):
    pass
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     for field_name, field in self.fields.items():
    #         if isinstance(field, serializers.ImageField):
    #             value = getattr(instance, field_name)
    #             if value:
    #                 try:
    #                     if not os.path.isfile(value.path):
    #                         model_field = instance._meta.get_field(field_name)

    #                         if model_field.null:  
    #                             setattr(instance, field_name, None)
    #                             instance.save(update_fields=[field_name])
    #                             data[field_name] = None
    #                         else:
    #                             data[field_name] = None

    #                 except (ValueError, OSError):
    #                     model_field = instance._meta.get_field(field_name)

    #                     if model_field.null:
    #                         setattr(instance, field_name, None)
    #                         instance.save(update_fields=[field_name])
    #                         data[field_name] = None
    #                     else:
    #                         data[field_name] = None

    #     return data
    



class BaseErrorResponseSerializer(serializers.Serializer):
    message = serializers.JSONField(allow_null=True, default=None)