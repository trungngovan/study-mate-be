"""
URL configuration for dashboard app.
"""
from django.urls import path
from .views import dashboard_statistics

app_name = 'dashboard'

urlpatterns = [
    path('statistics/', dashboard_statistics, name='dashboard-statistics'),
]


