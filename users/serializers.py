"""
Serializers for user location and location history.
"""
from rest_framework import serializers
from locations.models import LocationHistory


class LocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating user location.
    """
    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text="Latitude coordinate (-90 to 90)"
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text="Longitude coordinate (-180 to 180)"
    )
    accuracy = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="GPS accuracy in meters"
    )
    
    def validate(self, attrs):
        """Validate location coordinates."""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        # Additional validation: check if coordinates make sense
        if latitude == 0 and longitude == 0:
            raise serializers.ValidationError(
                "Invalid location: coordinates cannot both be 0."
            )
        
        return attrs


class LocationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for location history records.
    """
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = LocationHistory
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'latitude',
            'longitude',
            'recorded_at',
            'accuracy',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'user_email', 'user_name']
    
    def get_latitude(self, obj):
        """Extract latitude from geom_point."""
        if obj.geom_point:
            return obj.geom_point.y
        return None
    
    def get_longitude(self, obj):
        """Extract longitude from geom_point."""
        if obj.geom_point:
            return obj.geom_point.x
        return None


class LocationHistoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for location history list view.
    """
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = LocationHistory
        fields = [
            'id',
            'latitude',
            'longitude',
            'recorded_at',
            'accuracy'
        ]
        read_only_fields = ['id']
    
    def get_latitude(self, obj):
        """Extract latitude from geom_point."""
        if obj.geom_point:
            return obj.geom_point.y
        return None
    
    def get_longitude(self, obj):
        """Extract longitude from geom_point."""
        if obj.geom_point:
            return obj.geom_point.x
        return None


class CurrentLocationSerializer(serializers.Serializer):
    """
    Serializer for current user location (from User.geom_last_point).
    """
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    last_updated = serializers.DateTimeField(source='updated_at', allow_null=True)
    
    class Meta:
        fields = ['latitude', 'longitude', 'last_updated']


class LocationStatsSerializer(serializers.Serializer):
    """
    Serializer for location statistics.
    """
    total_records = serializers.IntegerField()
    days_analyzed = serializers.IntegerField()
    first_recorded = serializers.DateTimeField(required=False)
    last_recorded = serializers.DateTimeField(required=False)
    current_location = serializers.DictField()
    message = serializers.CharField(required=False)


class NearbyLearnerSerializer(serializers.Serializer):
    """
    Serializer for nearby learner information.
    """
    id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    avatar_url = serializers.URLField(allow_null=True)
    bio = serializers.CharField()
    school_name = serializers.CharField(source='school.name', allow_null=True)
    major = serializers.CharField(allow_null=True)
    year = serializers.IntegerField(allow_null=True)
    distance_km = serializers.FloatField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
