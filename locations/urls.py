from django.urls import path
from locations.views import (
    SchoolListCreateAPIView,
    SchoolRetrieveUpdateDestroyAPIView,
    SchoolSearchByLocationAPIView,
    SchoolListByCityAPIView,
    CityListCreateAPIView,
    CityRetrieveUpdateDestroyAPIView,
    CitySearchByLocationAPIView,
)

app_name = "locations"

urlpatterns = [
    # School endpoints
    path("schools/", SchoolListCreateAPIView.as_view(), name="school-list-create"),
    path("schools/<int:pk>/", SchoolRetrieveUpdateDestroyAPIView.as_view(), name="school-detail"),
    path("schools/search/location/", SchoolSearchByLocationAPIView.as_view(), name="school-search-location"),
    path("schools/search/city/", SchoolListByCityAPIView.as_view(), name="school-search-city"),
    
    # City endpoints
    path("cities/", CityListCreateAPIView.as_view(), name="city-list-create"),
    path("cities/<int:pk>/", CityRetrieveUpdateDestroyAPIView.as_view(), name="city-detail"),
    path("cities/search/location/", CitySearchByLocationAPIView.as_view(), name="city-search-location"),
]
