"""
OpenAPI schema definitions for user location endpoints.
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from users.serializers import (
    LocationUpdateSerializer,
    LocationHistorySerializer,
    LocationHistoryListSerializer,
    LocationStatsSerializer,
    NearbyLearnerSerializer
)


# Response serializers for documentation
LocationUpdateResponseSerializer = inline_serializer(
    name='LocationUpdateResponse',
    fields={
        'updated': serializers.BooleanField(),
        'saved_to_history': serializers.BooleanField(),
        'distance_moved': serializers.FloatField(allow_null=True),
        'time_since_last': serializers.FloatField(allow_null=True),
        'message': serializers.CharField(),
        'latitude': serializers.FloatField(),
        'longitude': serializers.FloatField(),
        'timestamp': serializers.DateTimeField(),
    }
)


# Schema decorators
update_location_schema = extend_schema(
    summary="Update user location",
    description="""
    Update the authenticated user's current location (geom_last_point).
    
    **Location History Tracking:**
    - Saves to LocationHistory if user moved >100 meters from last saved location
    - OR if >15 minutes passed since last saved location
    - Always updates User.geom_last_point regardless of threshold
    
    **Response includes:**
    - Whether location was saved to history
    - Distance moved (if applicable)
    - Time since last update (if applicable)
    - Descriptive message about the action taken
    """,
    request=LocationUpdateSerializer,
    responses={
        200: LocationUpdateResponseSerializer,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        },
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["User Location"]
)

current_location_schema = extend_schema(
    summary="Get current location",
    description="Retrieve the authenticated user's last known location from User.geom_last_point.",
    responses={
        200: inline_serializer(
            name='CurrentLocationResponse',
            fields={
                'latitude': serializers.FloatField(allow_null=True),
                'longitude': serializers.FloatField(allow_null=True),
                'last_updated': serializers.DateTimeField(allow_null=True),
                'message': serializers.CharField(required=False),
            }
        ),
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["User Location"]
)

location_history_list_schema = extend_schema(
    summary="List location history",
    description="""
    Retrieve paginated list of location history records for the authenticated user.
    
    **Note:** Only returns locations that were saved to history based on the 100m/15min threshold.
    """,
    parameters=[
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Maximum number of records to return (default: 50)",
            required=False
        ),
        OpenApiParameter(
            name="from_date",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description="Filter records from this date (ISO 8601 format)",
            required=False
        ),
        OpenApiParameter(
            name="to_date",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description="Filter records to this date (ISO 8601 format)",
            required=False
        ),
    ],
    responses={
        200: LocationHistoryListSerializer(many=True),
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["User Location"]
)

location_history_detail_schema = extend_schema(
    summary="Get location history detail",
    description="Retrieve detailed information about a specific location history record.",
    responses={
        200: LocationHistorySerializer,
        404: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Not found."}
            }
        },
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["User Location"]
)

location_stats_schema = extend_schema(
    summary="Get location statistics",
    description="""
    Retrieve statistics about the authenticated user's location history.
    
    Includes:
    - Total number of location records
    - Date range of records
    - Current location coordinates
    """,
    parameters=[
        OpenApiParameter(
            name="days",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of days to analyze (default: 30)",
            required=False
        ),
    ],
    responses={
        200: LocationStatsSerializer,
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["User Location"]
)

nearby_learners_response = inline_serializer(
    name='NearbyLearnersResponse',
    fields={
        'radius_km': serializers.FloatField(),
        'count': serializers.IntegerField(),
        'learners': NearbyLearnerSerializer(many=True),
    }
)

nearby_learners_schema = extend_schema(
    summary="Discover nearby learners",
    description="""
    Find other learners within a specified radius of your current location.
    
    **Features:**
    - Uses your current location (geom_last_point)
    - Filters active users only
    - Orders results by distance (closest first)
    - Returns up to 50 nearby learners
    
    **Radius:**
    - Provide custom radius in km via query parameter
    - Defaults to your learning_radius_km preference if not specified
    """,
    parameters=[
        OpenApiParameter(
            name="radius",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Search radius in kilometers (default: user's learning_radius_km)",
            required=False
        ),
    ],
    responses={
        200: nearby_learners_response,
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "No location data available for current user"},
                "learners": {"type": "array", "items": {}},
                "count": {"type": "integer", "example": 0}
            }
        },
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["Discover"]
)
