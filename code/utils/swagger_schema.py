# schema.py
from drf_spectacular.utils import OpenApiResponse
from rest_framework import serializers
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes



# Pagination parameters (used in list views)
pagination_parameters = [
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Page number"
    )
]

def get_paginated_response(custom_serializer):
    class PaginatedResponseSerializer(serializers.Serializer):
        message = serializers.CharField()
        count = serializers.IntegerField()
        next = serializers.CharField(allow_null=True)
        previous = serializers.CharField(allow_null=True)
        data = custom_serializer(many=True)

        class Meta:
            ref_name = f'PaginatedResponse_{custom_serializer.__name__}'
    return PaginatedResponseSerializer


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()



# 200 OK
ok_200 = OpenApiResponse(
    description="Successful response"
)

# 201 Created
created_201 = OpenApiResponse(
    description="Resource created successfully"
)

# 204 No Content
no_content_204 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Successfully deleted. No content to return."
)

# 205 Reset Content
reset_205 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Reset content. Typically used for logout or token reset."
)

# 400 Bad Request
error_400 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Bad Request – Invalid input or missing fields"
)

# 401 Unauthorized
error_401 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Unauthorized – Authentication required or failed"
)

# 403 Forbidden
error_403 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Forbidden – You don't have permission to access this resource"
)

# 404 Not Found
error_404 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Not Found – The requested resource was not found"
)

# 405 Method Not Allowed
error_405 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Method Not Allowed – Method ... not allowed."
)


# 500 Internal Server Error
error_500 = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Internal Server Error – Unexpected issue on server"
)

api_key_parameter = OpenApiParameter(name='X-Api-Key', location=OpenApiParameter.HEADER, required=True, type=str)