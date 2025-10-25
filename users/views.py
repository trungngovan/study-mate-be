"""
API views for user location management.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q

from locations.models import LocationHistory
from users.models import User
from users.serializers import (
    LocationUpdateSerializer,
    LocationHistorySerializer,
    LocationHistoryListSerializer,
    LocationStatsSerializer,
    NearbyLearnerSerializer
)
from users.services import LocationUpdateService
from users.schema import (
    update_location_schema,
    current_location_schema,
    location_history_list_schema,
    location_history_detail_schema,
    location_stats_schema,
    nearby_learners_schema
)
from matching.models import Connection


class UpdateLocationView(APIView):
    """
    API endpoint to update user's current location.
    
    POST: Update user's geom_last_point and conditionally save to LocationHistory
          based on 100m/15min threshold.
    """
    permission_classes = [IsAuthenticated]
    
    @update_location_schema
    @method_decorator(never_cache)
    def post(self, request):
        """
        Update user location.
        
        Request body:
        - latitude: float (required)
        - longitude: float (required)
        - accuracy: float (optional) - GPS accuracy in meters
        
        Returns:
        - updated: bool
        - saved_to_history: bool
        - distance_moved: float (meters)
        - time_since_last: float (seconds)
        - message: str
        - latitude: float
        - longitude: float
        - timestamp: ISO datetime string
        """
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract validated data
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        accuracy = serializer.validated_data.get('accuracy')
        
        # Use service to update location
        location_service = LocationUpdateService(request.user)
        result = location_service.update_location(
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy
        )
        
        return Response(result, status=status.HTTP_200_OK)


class CurrentLocationView(APIView):
    """
    API endpoint to get user's current location.
    
    GET: Retrieve user's last known location from User.geom_last_point
    """
    permission_classes = [IsAuthenticated]
    
    @current_location_schema
    def get(self, request):
        """Get current user location."""
        user = request.user
        
        if not user.geom_last_point:
            return Response({
                'latitude': None,
                'longitude': None,
                'last_updated': None,
                'message': 'No location data available'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'latitude': user.geom_last_point.y,
            'longitude': user.geom_last_point.x,
            'last_updated': user.updated_at.isoformat() if user.updated_at else None,
        }, status=status.HTTP_200_OK)


@location_history_list_schema
class LocationHistoryListView(generics.ListAPIView):
    """
    API endpoint to list user's location history.
    
    GET: Retrieve paginated list of location history records for the current user.
    
    Query parameters:
    - limit: int (default: 50) - Maximum number of records
    - from_date: ISO datetime - Filter from this date
    - to_date: ISO datetime - Filter to this date
    """
    serializer_class = LocationHistoryListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter location history for current user."""
        user = self.request.user
        limit = int(self.request.query_params.get('limit', 50))
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        location_service = LocationUpdateService(user)
        return location_service.get_location_history(
            limit=limit,
            from_date=from_date,
            to_date=to_date
        )


@location_history_detail_schema
class LocationHistoryDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a specific location history record.
    
    GET: Retrieve detailed information about a location history entry.
    """
    serializer_class = LocationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only allow users to access their own location history."""
        return LocationHistory.objects.filter(user=self.request.user)


class LocationStatsView(APIView):
    """
    API endpoint to get location statistics.
    
    GET: Retrieve statistics about user's location history.
    
    Query parameters:
    - days: int (default: 30) - Number of days to analyze
    """
    permission_classes = [IsAuthenticated]
    
    @location_stats_schema
    def get(self, request):
        """Get location statistics."""
        days = int(request.query_params.get('days', 30))
        
        location_service = LocationUpdateService(request.user)
        stats = location_service.get_location_stats(days=days)
        
        serializer = LocationStatsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class NearbyLearnersView(generics.ListAPIView):
    """
    API endpoint to discover nearby learners.
    
    GET: Find users within a specified radius of the current user's location.
    
    Query parameters:
    - radius: float (optional, default: user's learning_radius_km) - Search radius in kilometers
    """
    serializer_class = NearbyLearnerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get nearby learners within specified radius, excluding existing connections and connection requests."""
        user = self.request.user
        
        # Check if user has location data
        if not user.geom_last_point:
            return User.objects.none()
        
        # Get radius from query params or use user's default
        try:
            radius_km = float(self.request.query_params.get('radius', user.learning_radius_km))
        except (ValueError, TypeError):
            radius_km = user.learning_radius_km
        
        # Store radius for use in list method
        self._radius_km = radius_km
        
        # Get list of connected user IDs (accepted connections)
        # Connection model stores user1_id < user2_id, so we need to check both columns
        connected_user_ids = set()
        connections = Connection.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).select_related('user1', 'user2')
        
        for conn in connections:
            # Add the other user's ID (not the current user's ID)
            if conn.user1_id == user.id:
                connected_user_ids.add(conn.user2_id)
            else:
                connected_user_ids.add(conn.user1_id)
        
        # Get list of user IDs with existing connection requests (in any direction, any state)
        # This prevents showing users who already have pending, rejected, or any connection request
        from matching.models import ConnectionRequest
        connection_request_user_ids = set()
        
        # Get all connection requests where user is sender or receiver
        connection_requests = ConnectionRequest.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).values_list('sender_id', 'receiver_id')
        
        for sender_id, receiver_id in connection_requests:
            # Add the other user's ID (not the current user's ID)
            if sender_id == user.id:
                connection_request_user_ids.add(receiver_id)
            else:
                connection_request_user_ids.add(sender_id)
        
        # Query nearby users using PostGIS distance function
        # Exclude current user, already connected users, and users with existing connection requests
        nearby_users = User.objects.filter(
            geom_last_point__isnull=False,
            status=User.STATUS_ACTIVE
        ).exclude(
            id=user.id
        ).exclude(
            id__in=connected_user_ids
        ).exclude(
            id__in=connection_request_user_ids
        ).filter(
            geom_last_point__dwithin=(user.geom_last_point, D(km=radius_km))
        ).annotate(
            distance=Distance('geom_last_point', user.geom_last_point)
        ).order_by('distance')
        
        return nearby_users
    
    @nearby_learners_schema
    def list(self, request, *args, **kwargs):
        """Override list to add custom response wrapper and validate location."""
        user = request.user
        
        # Check if user has location data
        if not user.geom_last_point:
            return Response({
                'error': 'No location data available for current user',
                'radius_km': 0,
                'count': 0,
                'results': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Convert queryset to data with distance
            learners_data = []
            for nearby_user in page:
                learner_data = {
                    'id': nearby_user.id,
                    'email': nearby_user.email,
                    'full_name': nearby_user.full_name,
                    'avatar_url': nearby_user.avatar_url,
                    'bio': nearby_user.bio,
                    'school': nearby_user.school,
                    'major': nearby_user.major,
                    'year': nearby_user.year,
                    'distance_km': round(nearby_user.distance.km, 2),
                    'latitude': nearby_user.geom_last_point.y,
                    'longitude': nearby_user.geom_last_point.x,
                }
                learners_data.append(learner_data)
            
            serializer = self.get_serializer(learners_data, many=True)
            
            # Get paginated response
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Add custom fields to the response
            paginated_response.data['radius_km'] = getattr(self, '_radius_km', user.learning_radius_km)
            
            return paginated_response
        
        # Non-paginated response (shouldn't happen with default settings)
        learners_data = []
        for nearby_user in queryset:
            learner_data = {
                'id': nearby_user.id,
                'email': nearby_user.email,
                'full_name': nearby_user.full_name,
                'avatar_url': nearby_user.avatar_url,
                'bio': nearby_user.bio,
                'school': nearby_user.school,
                'major': nearby_user.major,
                'year': nearby_user.year,
                'distance_km': round(nearby_user.distance.km, 2),
                'latitude': nearby_user.geom_last_point.y,
                'longitude': nearby_user.geom_last_point.x,
            }
            learners_data.append(learner_data)
        
        serializer = self.get_serializer(learners_data, many=True)
        
        return Response({
            'radius_km': getattr(self, '_radius_km', user.learning_radius_km),
            'count': len(learners_data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

