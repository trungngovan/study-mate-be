from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.response import Response
from rest_framework import status

from locations.models import School
from locations.serializers import (
    SchoolListSerializer,
    SchoolDetailSerializer,
    SchoolCreateUpdateSerializer,
)
from locations.schema import (
    school_list_schema,
    school_create_schema,
    school_retrieve_schema,
    school_update_schema,
    school_partial_update_schema,
    school_delete_schema,
    school_search_by_location_schema,
    school_list_by_city_schema,
)


class SchoolListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all schools or create a new school.
    
    GET: List all schools with pagination and search (requires authentication)
    POST: Create a new school (requires authentication)
    """
    queryset = School.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "short_name", "city", "address"]
    ordering_fields = ["name", "city", "created_at"]
    
    @school_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @school_create_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == "POST":
            return SchoolCreateUpdateSerializer
        return SchoolListSerializer
    
    def get_queryset(self):
        """
        Optionally filter schools by city or country.
        Also supports proximity search if lat/lng provided.
        """
        queryset = super().get_queryset()
        
        # Filter by city
        city = self.request.query_params.get("city", None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by country
        country = self.request.query_params.get("country", None)
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        # Proximity search
        latitude = self.request.query_params.get("lat", None)
        longitude = self.request.query_params.get("lng", None)
        radius_km = self.request.query_params.get("radius", 10)  # Default 10km
        
        if latitude and longitude:
            try:
                user_location = Point(float(longitude), float(latitude), srid=4326)
                queryset = queryset.filter(geom_point__isnull=False).annotate(
                    distance=Distance("geom_point", user_location)
                ).filter(distance__lte=float(radius_km) * 1000).order_by("distance")
            except (ValueError, TypeError):
                pass
        
        return queryset


class SchoolRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a school.
    
    GET: Retrieve a single school by ID (requires authentication)
    PUT/PATCH: Update a school (requires authentication)
    DELETE: Delete a school (requires authentication)
    """
    queryset = School.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    @school_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @school_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @school_partial_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @school_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for retrieve and update."""
        if self.request.method in ["PUT", "PATCH"]:
            return SchoolCreateUpdateSerializer
        return SchoolDetailSerializer


@school_search_by_location_schema
class SchoolSearchByLocationAPIView(generics.ListAPIView):
    """
    API view to search schools by geographic location.
    
    Query params:
    - lat: Latitude (required)
    - lng: Longitude (required)
    - radius: Search radius in kilometers (default: 10)
    (requires authentication)
    """
    serializer_class = SchoolDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter schools within radius of given location."""
        latitude = self.request.query_params.get("lat")
        longitude = self.request.query_params.get("lng")
        radius_km = float(self.request.query_params.get("radius", 10))
        
        if not latitude or not longitude:
            return School.objects.none()
        
        try:
            user_location = Point(float(longitude), float(latitude), srid=4326)
            queryset = School.objects.filter(geom_point__isnull=False).annotate(
                distance=Distance("geom_point", user_location)
            ).filter(distance__lte=radius_km * 1000).order_by("distance")
            
            return queryset
        except (ValueError, TypeError):
            return School.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Override to add distance information to response."""
        latitude = request.query_params.get("lat")
        longitude = request.query_params.get("lng")
        
        if not latitude or not longitude:
            return Response(
                {"error": "Both 'lat' and 'lng' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            
            # Add distance information
            for i, school in enumerate(page):
                if hasattr(school, "distance"):
                    data[i]["distance_km"] = round(school.distance.km, 2)
            
            return self.get_paginated_response(data)
        
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # Add distance information
        for i, school in enumerate(queryset):
            if hasattr(school, "distance"):
                data[i]["distance_km"] = round(school.distance.km, 2)
        
        return Response(data)


@school_list_by_city_schema
class SchoolListByCityAPIView(generics.ListAPIView):
    """
    API view to list schools grouped by city.
    
    Query params:
    - city: City name (required)
    (requires authentication)
    """
    serializer_class = SchoolListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter schools by city."""
        city = self.request.query_params.get("city")
        
        if not city:
            return School.objects.none()
        
        return School.objects.filter(city__icontains=city).order_by("name")
    
    def list(self, request, *args, **kwargs):
        """Override to validate city parameter."""
        city = request.query_params.get("city")
        
        if not city:
            return Response(
                {"error": "The 'city' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().list(request, *args, **kwargs)
  