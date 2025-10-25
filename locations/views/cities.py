from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.response import Response
from rest_framework import status

from locations.models import City
from locations.serializers import (
    CityListSerializer,
    CityDetailSerializer,
    CityCreateUpdateSerializer,
)
from locations.schema import (
    city_list_schema,
    city_create_schema,
    city_retrieve_schema,
    city_update_schema,
    city_partial_update_schema,
    city_delete_schema,
    city_search_by_location_schema,
)


class CityListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all cities or create a new city.
    
    GET: List all cities with pagination and search (requires authentication)
    POST: Create a new city (requires authentication)
    """
    queryset = City.objects.all().order_by("name")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    
    @city_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @city_create_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == "POST":
            return CityCreateUpdateSerializer
        return CityListSerializer
    
    def get_queryset(self):
        """
        Optionally supports proximity search if lat/lng provided.
        """
        queryset = super().get_queryset()
        
        # Proximity search
        latitude = self.request.query_params.get("lat", None)
        longitude = self.request.query_params.get("lng", None)
        radius_km = self.request.query_params.get("radius", 50)  # Default 50km
        
        if latitude and longitude:
            try:
                user_location = Point(float(longitude), float(latitude), srid=4326)
                queryset = queryset.filter(geom_point__isnull=False).annotate(
                    distance=Distance("geom_point", user_location)
                ).filter(distance__lte=float(radius_km) * 1000).order_by("distance")
            except (ValueError, TypeError):
                pass
        
        return queryset


class CityRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a city.
    
    GET: Retrieve a single city by ID (requires authentication)
    PUT/PATCH: Update a city (requires authentication)
    DELETE: Delete a city (requires authentication)
    """
    queryset = City.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    @city_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @city_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @city_partial_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @city_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for retrieve and update."""
        if self.request.method in ["PUT", "PATCH"]:
            return CityCreateUpdateSerializer
        return CityDetailSerializer


@city_search_by_location_schema
class CitySearchByLocationAPIView(generics.ListAPIView):
    """
    API view to search cities by geographic location.
    
    Query params:
    - lat: Latitude (required)
    - lng: Longitude (required)
    - radius: Search radius in kilometers (default: 50)
    (requires authentication)
    """
    serializer_class = CityDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter cities within radius of given location."""
        latitude = self.request.query_params.get("lat")
        longitude = self.request.query_params.get("lng")
        radius_km = float(self.request.query_params.get("radius", 50))
        
        if not latitude or not longitude:
            return City.objects.none()
        
        try:
            user_location = Point(float(longitude), float(latitude), srid=4326)
            queryset = City.objects.filter(geom_point__isnull=False).annotate(
                distance=Distance("geom_point", user_location)
            ).filter(distance__lte=radius_km * 1000).order_by("distance")
            
            return queryset
        except (ValueError, TypeError):
            return City.objects.none()
    
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
            for i, city in enumerate(page):
                if hasattr(city, "distance"):
                    data[i]["distance_km"] = round(city.distance.km, 2)
            
            return self.get_paginated_response(data)
        
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # Add distance information
        for i, city in enumerate(queryset):
            if hasattr(city, "distance"):
                data[i]["distance_km"] = round(city.distance.km, 2)
        
        return Response(data)
