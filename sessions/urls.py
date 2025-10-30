"""
URL configuration for sessions app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudySessionViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'', StudySessionViewSet, basename='study-session')

urlpatterns = [
    path('', include(router.urls)),
]
