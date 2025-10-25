from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from locations.models import City


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for City model.
    """
    school_count = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "school_count",
        ]
        read_only_fields = ["id", "school_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_school_count(self, obj) -> int:
        """Return the number of schools in this city."""
        return obj.schools.count()


class CityListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for City list view.
    """
    school_count = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "school_count",
        ]
        read_only_fields = ["id", "school_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_school_count(self, obj) -> int:
        """Return the number of schools in this city."""
        return obj.schools.count()


class CityDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for City with geographic data.
    """
    school_count = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "school_count",
        ]
        read_only_fields = ["id", "school_count", "latitude", "longitude"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_school_count(self, obj) -> int:
        """Return the number of schools in this city."""
        return obj.schools.count()
    
    @extend_schema_field(serializers.FloatField)
    def get_latitude(self, obj):
        """Extract latitude from geom_point."""
        if obj.geom_point:
            return obj.geom_point.y
        return None
    
    @extend_schema_field(serializers.FloatField)
    def get_longitude(self, obj):
        """Extract longitude from geom_point."""
        if obj.geom_point:
            return obj.geom_point.x
        return None


class CityCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating City with geographic point support.
    """
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id"]
    
    def create(self, validated_data):
        """Create a city with geographic point from lat/lng."""
        from django.contrib.gis.geos import Point
        
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)
        
        city = City(**validated_data)
        
        if latitude is not None and longitude is not None:
            city.geom_point = Point(longitude, latitude, srid=4326)
        
        city.save()
        return city
    
    def update(self, instance, validated_data):
        """Update a city with geographic point from lat/lng."""
        from django.contrib.gis.geos import Point
        
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if latitude is not None and longitude is not None:
            instance.geom_point = Point(longitude, latitude, srid=4326)
        
        instance.save()
        return instance
