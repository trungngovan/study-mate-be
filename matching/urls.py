"""
URL configuration for matching app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ConnectionRequestViewSet, ConnectionViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'requests', ConnectionRequestViewSet, basename='connection-request')
router.register(r'connections', ConnectionViewSet, basename='connection')

urlpatterns = [
    path('', include(router.urls)),
]
