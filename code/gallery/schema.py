from drf_spectacular.utils import OpenApiParameter



martyr_search_parameter = OpenApiParameter(
    name='martyr',
    type=int,
    location=OpenApiParameter.QUERY,
    description="Search galleries by martyr ID",
    required=False
)