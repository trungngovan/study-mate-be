from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from locations.models import School


class SchoolSerializer(serializers.ModelSerializer):
    """
    Serializer for School model.
    """
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "short_name",
            "address",
            "city",
            "website",
            "email",
            "phone",
            "created_at",
            "updated_at",
            "student_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "student_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_student_count(self, obj) -> int:
        """Return the number of students enrolled in this school."""
        return obj.students.filter(status="active").count()


class SchoolListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for School list view.
    """
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "short_name",
            "city",
            "student_count",
        ]
        read_only_fields = ["id", "student_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_student_count(self, obj) -> int:
        """Return the number of students enrolled in this school."""
        return obj.students.filter(status="active").count()


class SchoolDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for School with geographic data.
    """
    student_count = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "short_name",
            "address",
            "city",
            "latitude",
            "longitude",
            "website",
            "email",
            "phone",
            "created_at",
            "updated_at",
            "student_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "student_count", "latitude", "longitude"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_student_count(self, obj) -> int:
        """Return the number of students enrolled in this school."""
        return obj.students.filter(status="active").count()
    
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


class SchoolCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating School with geographic point support.
    """
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "short_name",
            "address",
            "city",
            "latitude",
            "longitude",
            "website",
            "email",
            "phone",
        ]
        read_only_fields = ["id"]
    
    def create(self, validated_data):
        """Create a school with geographic point from lat/lng."""
        from django.contrib.gis.geos import Point
        
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)
        
        school = School(**validated_data)
        
        if latitude is not None and longitude is not None:
            school.geom_point = Point(longitude, latitude, srid=4326)
        
        school.save()
        return school
    
    def update(self, instance, validated_data):
        """Update a school with geographic point from lat/lng."""
        from django.contrib.gis.geos import Point
        
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if latitude is not None and longitude is not None:
            instance.geom_point = Point(longitude, latitude, srid=4326)
        
        instance.save()
        return instance
