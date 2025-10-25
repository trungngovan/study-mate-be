"""
URL configuration for users app.
"""
from django.urls import path
from users.views import (
    UpdateLocationView,
    CurrentLocationView,
    LocationHistoryListView,
    LocationHistoryDetailView,
    LocationStatsView,
    NearbyLearnersView
)

app_name = 'users'

urlpatterns = [
    # Location update endpoints
    path('location/', UpdateLocationView.as_view(), name='update-location'),
    path('location/current/', CurrentLocationView.as_view(), name='current-location'),
    
    # Location history endpoints
    path('location/history/', LocationHistoryListView.as_view(), name='location-history'),
    path('location/history/<int:pk>/', LocationHistoryDetailView.as_view(), name='location-history-detail'),
    
    # Location statistics
    path('location/stats/', LocationStatsView.as_view(), name='location-stats'),
]
