"""
URL configuration for groups app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudyGroupViewSet, GroupMembershipViewSet, GroupMessageViewSet


# Create router and register viewsets
router = DefaultRouter()
router.register(r'', StudyGroupViewSet, basename='study-group')
router.register(r'memberships', GroupMembershipViewSet, basename='group-membership')

# Group-specific message endpoints (nested)
urlpatterns = [
    path('', include(router.urls)),
    path('<int:group_id>/messages/', GroupMessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='group-messages'),
    path('<int:group_id>/messages/mark_read/', GroupMessageViewSet.as_view({'post': 'mark_read'}), name='group-messages-mark-read'),
]
