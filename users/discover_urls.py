"""
URL configuration for discover endpoints.
"""
from django.urls import path
from users.views import NearbyLearnersView

app_name = 'discover'

urlpatterns = [
    path('nearby-learners/', NearbyLearnersView.as_view(), name='nearby-learners'),
]
