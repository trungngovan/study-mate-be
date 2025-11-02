"""
Serializers for dashboard statistics.
"""
from rest_framework import serializers


class SessionStatisticsSerializer(serializers.Serializer):
    """Serializer for session statistics."""
    
    # Hosting statistics
    sessions_hosted_total = serializers.IntegerField()
    sessions_hosted_upcoming = serializers.IntegerField()
    sessions_hosted_in_progress = serializers.IntegerField()
    sessions_hosted_completed = serializers.IntegerField()
    sessions_hosted_cancelled = serializers.IntegerField()
    
    # Attending statistics
    sessions_attending_total = serializers.IntegerField()
    sessions_attending_upcoming = serializers.IntegerField()
    sessions_attending_in_progress = serializers.IntegerField()
    sessions_attending_completed = serializers.IntegerField()
    
    # Participation statistics
    total_participations = serializers.IntegerField()
    participations_attended = serializers.IntegerField()
    participations_registered = serializers.IntegerField()
    participations_no_show = serializers.IntegerField()
    participations_cancelled = serializers.IntegerField()
    
    # Session type breakdown
    sessions_by_type = serializers.DictField(child=serializers.IntegerField())
    
    # Total participants across all hosted sessions
    total_participants_in_hosted_sessions = serializers.IntegerField()


class ConnectionStatisticsSerializer(serializers.Serializer):
    """Serializer for connection statistics."""
    
    sent_pending = serializers.IntegerField()
    received_pending = serializers.IntegerField()
    accepted_connections = serializers.IntegerField()
    total_requests = serializers.IntegerField()


class DashboardStatisticsSerializer(serializers.Serializer):
    """Serializer for complete dashboard statistics."""
    
    sessions = SessionStatisticsSerializer()
    connections = ConnectionStatisticsSerializer()


