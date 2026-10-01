from drf_spectacular.utils import OpenApiParameter


name_search_parameter = OpenApiParameter(
    name='name',
    type=str, 
    location=OpenApiParameter.QUERY, 
    description="Search Martyrs by name(case-insensitive)", 
    required=False)

biography_search_parameter = OpenApiParameter(
    name='biography',
    type=str, 
    location=OpenApiParameter.QUERY, 
    description="Search Martyrs by biography(case-insensitive)", 
    required=False)


narrative_search_parameter = OpenApiParameter(
    name='narrative',
    type=str, 
    location=OpenApiParameter.QUERY, 
    description="Search Martyrs by narrative(case-insensitive)", 
    required=False)

testament_search_parameter = OpenApiParameter(
    name='testament',
    type=str, 
    location=OpenApiParameter.QUERY, 
    description="Search Martyrs by testament(case-insensitive)", 
    required=False)

pilgrimage_letter_search_parameter = OpenApiParameter(
    name='pilgrimage_letter',
    type=str,
    location=OpenApiParameter.QUERY, 
    description="Search Martyrs by pilgrimage letter(case-insensitive)", 
    required=False)