"""
OpenAPI schema definitions for locations endpoints.
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from .serializers import (
    SchoolListSerializer,
    SchoolDetailSerializer,
    SchoolCreateUpdateSerializer,
    CityListSerializer,
    CityDetailSerializer,
    CityCreateUpdateSerializer,
)


# Schema for error response
ErrorResponseSerializer = inline_serializer(
    name='LocationErrorResponse',
    fields={
        'error': serializers.CharField(),
    }
)


# School List/Create schemas
school_list_schema = extend_schema(
    summary="List schools",
    description="Get a paginated list of schools. Supports search, filtering, and proximity-based queries.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search schools by name, short_name, city, or address"
        ),
        OpenApiParameter(
            name="city",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter schools by city name"
        ),
        OpenApiParameter(
            name="lat",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Latitude for proximity search"
        ),
        OpenApiParameter(
            name="lng",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Longitude for proximity search"
        ),
        OpenApiParameter(
            name="radius",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Search radius in kilometers (default: 10)"
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: name, city, created_at (prefix with - for descending)"
        ),
    ],
    responses={200: SchoolListSerializer(many=True)},
    tags=["Schools"]
)

school_create_schema = extend_schema(
    summary="Create a school",
    description="Create a new school. Requires authentication. Optionally include latitude and longitude for geographic location.",
    request=SchoolCreateUpdateSerializer,
    responses={201: SchoolCreateUpdateSerializer},
    tags=["Schools"]
)


# School Retrieve/Update/Destroy schemas
school_retrieve_schema = extend_schema(
    summary="Get school details",
    description="Retrieve detailed information about a specific school including geographic coordinates.",
    responses={200: SchoolDetailSerializer},
    tags=["Schools"]
)

school_update_schema = extend_schema(
    summary="Update school (full)",
    description="Fully update a school's information. Requires authentication.",
    request=SchoolCreateUpdateSerializer,
    responses={200: SchoolCreateUpdateSerializer},
    tags=["Schools"]
)

school_partial_update_schema = extend_schema(
    summary="Update school (partial)",
    description="Partially update a school's information. Requires authentication.",
    request=SchoolCreateUpdateSerializer,
    responses={200: SchoolCreateUpdateSerializer},
    tags=["Schools"]
)

school_delete_schema = extend_schema(
    summary="Delete school",
    description="Delete a school. Requires authentication.",
    responses={204: None},
    tags=["Schools"]
)


# School search by location schema
school_search_by_location_schema = extend_schema(
    summary="Search schools by location",
    description="Search for schools within a specified radius of a geographic location. Returns schools ordered by distance.",
    parameters=[
        OpenApiParameter(
            name="lat",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Latitude of the search center"
        ),
        OpenApiParameter(
            name="lng",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Longitude of the search center"
        ),
        OpenApiParameter(
            name="radius",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Search radius in kilometers (default: 10)"
        ),
    ],
    responses={
        200: SchoolDetailSerializer(many=True),
        400: ErrorResponseSerializer,
    },
    tags=["Schools"]
)


# School search by city schema
school_list_by_city_schema = extend_schema(
    summary="List schools by city",
    description="Get all schools in a specific city. Results are ordered alphabetically by school name.",
    parameters=[
        OpenApiParameter(
            name="city",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description="City name to filter schools"
        ),
    ],
    responses={
        200: SchoolListSerializer(many=True),
        400: ErrorResponseSerializer,
    },
    tags=["Schools"]
)


# City List/Create schemas
city_list_schema = extend_schema(
    summary="List cities",
    description="Get a paginated list of cities. Supports search, filtering, and proximity-based queries.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search cities by name"
        ),
        OpenApiParameter(
            name="lat",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Latitude for proximity search"
        ),
        OpenApiParameter(
            name="lng",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Longitude for proximity search"
        ),
        OpenApiParameter(
            name="radius",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Search radius in kilometers (default: 50)"
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: name (prefix with - for descending)"
        ),
    ],
    responses={200: CityListSerializer(many=True)},
    tags=["Cities"]
)

city_create_schema = extend_schema(
    summary="Create a city",
    description="Create a new city. Requires authentication. Optionally include latitude and longitude for geographic location.",
    request=CityCreateUpdateSerializer,
    responses={201: CityCreateUpdateSerializer},
    tags=["Cities"]
)


# City Retrieve/Update/Destroy schemas
city_retrieve_schema = extend_schema(
    summary="Get city details",
    description="Retrieve detailed information about a specific city including geographic coordinates.",
    responses={200: CityDetailSerializer},
    tags=["Cities"]
)

city_update_schema = extend_schema(
    summary="Update city (full)",
    description="Fully update a city's information. Requires authentication.",
    request=CityCreateUpdateSerializer,
    responses={200: CityCreateUpdateSerializer},
    tags=["Cities"]
)

city_partial_update_schema = extend_schema(
    summary="Update city (partial)",
    description="Partially update a city's information. Requires authentication.",
    request=CityCreateUpdateSerializer,
    responses={200: CityCreateUpdateSerializer},
    tags=["Cities"]
)

city_delete_schema = extend_schema(
    summary="Delete city",
    description="Delete a city. Requires authentication.",
    responses={204: None},
    tags=["Cities"]
)


# City search by location schema
city_search_by_location_schema = extend_schema(
    summary="Search cities by location",
    description="Search for cities within a specified radius of a geographic location. Returns cities ordered by distance.",
    parameters=[
        OpenApiParameter(
            name="lat",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Latitude of the search center"
        ),
        OpenApiParameter(
            name="lng",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Longitude of the search center"
        ),
        OpenApiParameter(
            name="radius",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Search radius in kilometers (default: 50)"
        ),
    ],
    responses={
        200: CityDetailSerializer(many=True),
        400: ErrorResponseSerializer,
    },
    tags=["Cities"]
)
