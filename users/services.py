"""
Service layer for user location management.
Implements business logic for location updates and history tracking.
"""
from datetime import timedelta
from django.utils import timezone
from django.contrib.gis.geos import Point
from locations.models import LocationHistory


class LocationUpdateService:
    """
    Service for handling user location updates with intelligent history tracking.
    
    Implements the 100m/15min threshold rule:
    - Save to LocationHistory if user moved more than 100 meters
    - OR if more than 15 minutes have passed since last update
    """
    
    DISTANCE_THRESHOLD_METERS = 100
    TIME_THRESHOLD_MINUTES = 15
    
    def __init__(self, user):
        """
        Initialize the service for a specific user.
        
        Args:
            user: User instance
        """
        self.user = user
    
    def update_location(self, latitude, longitude, accuracy=None):
        """
        Update user's location and conditionally save to history.
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            accuracy (float, optional): GPS accuracy in meters
        
        Returns:
            dict: Result containing:
                - updated: bool - Whether location was updated
                - saved_to_history: bool - Whether location was saved to history
                - distance_moved: float - Distance moved in meters (if applicable)
                - time_since_last: int - Seconds since last update (if applicable)
                - message: str - Description of the action taken
        """
        new_point = Point(longitude, latitude, srid=4326)
        current_time = timezone.now()
        
        should_save_to_history = False
        distance_moved = None
        time_since_last = None
        message = ""
        
        # Check if user has a previous location
        if self.user.geom_last_point:
            # Calculate distance moved
            distance_moved = self._calculate_distance(
                self.user.geom_last_point, 
                new_point
            )
            
            # Get last location history entry to check time threshold
            last_history = LocationHistory.objects.filter(
                user=self.user
            ).order_by('-recorded_at').first()
            
            if last_history:
                time_since_last = (current_time - last_history.recorded_at).total_seconds()
                
                # Check thresholds
                distance_threshold_met = distance_moved >= self.DISTANCE_THRESHOLD_METERS
                time_threshold_met = time_since_last >= (self.TIME_THRESHOLD_MINUTES * 60)
                
                if distance_threshold_met or time_threshold_met:
                    should_save_to_history = True
                    
                    if distance_threshold_met and time_threshold_met:
                        message = f"Location saved: moved {distance_moved:.1f}m and {time_since_last/60:.1f} minutes passed"
                    elif distance_threshold_met:
                        message = f"Location saved: moved {distance_moved:.1f}m (threshold: {self.DISTANCE_THRESHOLD_METERS}m)"
                    else:
                        message = f"Location saved: {time_since_last/60:.1f} minutes passed (threshold: {self.TIME_THRESHOLD_MINUTES} min)"
                else:
                    message = f"Location updated but not saved to history (moved {distance_moved:.1f}m in {time_since_last/60:.1f} min)"
            else:
                # No previous history, save the first entry
                should_save_to_history = True
                message = "First location recorded"
        else:
            # First time setting location
            should_save_to_history = True
            message = "Initial location set"
        
        # Update user's current location
        self.user.geom_last_point = new_point
        self.user.save(update_fields=['geom_last_point', 'updated_at'])
        
        # Save to history if threshold is met
        if should_save_to_history:
            LocationHistory.objects.create(
                user=self.user,
                geom_point=new_point,
                recorded_at=current_time,
                accuracy=accuracy
            )
        
        return {
            'updated': True,
            'saved_to_history': should_save_to_history,
            'distance_moved': distance_moved,
            'time_since_last': time_since_last,
            'message': message,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': current_time.isoformat()
        }
    
    def _calculate_distance(self, point1, point2):
        """
        Calculate distance between two geographic points in meters.
        
        Args:
            point1: First Point object
            point2: Second Point object
        
        Returns:
            float: Distance in meters
        """
        # Using PostGIS distance calculation (more accurate for geography)
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ST_Distance(
                    ST_GeogFromText(%s),
                    ST_GeogFromText(%s)
                )
            """, [point1.wkt, point2.wkt])
            result = cursor.fetchone()
            distance = result[0] if result else 0
        
        return distance
    
    def get_location_history(self, limit=50, from_date=None, to_date=None):
        """
        Get user's location history with optional filtering.
        
        Args:
            limit (int): Maximum number of records to return
            from_date (datetime, optional): Start date for filtering
            to_date (datetime, optional): End date for filtering
        
        Returns:
            QuerySet: Location history records
        """
        queryset = LocationHistory.objects.filter(user=self.user)
        
        if from_date:
            queryset = queryset.filter(recorded_at__gte=from_date)
        
        if to_date:
            queryset = queryset.filter(recorded_at__lte=to_date)
        
        return queryset[:limit]
    
    def get_location_stats(self, days=30):
        """
        Get statistics about user's location history.
        
        Args:
            days (int): Number of days to analyze
        
        Returns:
            dict: Statistics including total records, date range, etc.
        """
        since_date = timezone.now() - timedelta(days=days)
        
        history = LocationHistory.objects.filter(
            user=self.user,
            recorded_at__gte=since_date
        )
        
        count = history.count()
        
        if count == 0:
            return {
                'total_records': 0,
                'days_analyzed': days,
                'message': 'No location history found'
            }
        
        first_record = history.order_by('recorded_at').first()
        last_record = history.order_by('-recorded_at').first()
        
        stats = {
            'total_records': count,
            'days_analyzed': days,
            'current_location': {
                'latitude': self.user.geom_last_point.y if self.user.geom_last_point else None,
                'longitude': self.user.geom_last_point.x if self.user.geom_last_point else None,
            }
        }
        
        if first_record:
            stats['first_recorded'] = first_record.recorded_at.isoformat()
        
        if last_record:
            stats['last_recorded'] = last_record.recorded_at.isoformat()
        
        return stats
