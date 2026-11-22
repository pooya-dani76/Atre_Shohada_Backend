from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from .models import MarriageStatus, GraduationLevel


martyr_list_parameters = [
    OpenApiParameter(
        name="name",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Search by first name or last name",
        required=False,
    ),
    OpenApiParameter(
        name="dispatch",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Filter by dispatch type",
        required=False,
    ),
    OpenApiParameter(
        name="martyrdom",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Filter by martyrdom location",
        required=False,
    ),
    OpenApiParameter(
        name="graduation",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="Filter by education level",
        required=False,
        enum=GraduationLevel.values,
    ),
    OpenApiParameter(
        name="married",
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        description="Filter by marriage status (true for married, false for single)",
        required=False,
        enum=[True, False]
    ),
]