"""
Services for dashboard statistics.
"""
from django.db.models import Q
from sessions.models import StudySession, SessionParticipant


class SessionStatisticsService:
    """Service for calculating session statistics."""
    
    def __init__(self, user):
        self.user = user
    
    def get_statistics(self):
        """Get comprehensive session statistics for the user."""
        
        # Hosting statistics
        hosted_sessions = StudySession.objects.filter(host=self.user)
        
        sessions_hosted_total = hosted_sessions.count()
        sessions_hosted_upcoming = hosted_sessions.filter(
            status=StudySession.STATUS_UPCOMING
        ).count()
        sessions_hosted_in_progress = hosted_sessions.filter(
            status=StudySession.STATUS_IN_PROGRESS
        ).count()
        sessions_hosted_completed = hosted_sessions.filter(
            status=StudySession.STATUS_COMPLETED
        ).count()
        sessions_hosted_cancelled = hosted_sessions.filter(
            status=StudySession.STATUS_CANCELLED
        ).count()
        
        # Attending statistics (exclude sessions where user is the host)
        attending_participations = SessionParticipant.objects.filter(
            user=self.user,
            status__in=[
                SessionParticipant.STATUS_REGISTERED,
                SessionParticipant.STATUS_ATTENDED
            ]
        ).exclude(session__host=self.user)
        
        sessions_attending_total = attending_participations.values(
            'session'
        ).distinct().count()
        
        # Count by status
        attending_sessions = StudySession.objects.filter(
            participants__user=self.user,
            participants__status__in=[
                SessionParticipant.STATUS_REGISTERED,
                SessionParticipant.STATUS_ATTENDED
            ]
        ).exclude(host=self.user).distinct()
        
        sessions_attending_upcoming = attending_sessions.filter(
            status=StudySession.STATUS_UPCOMING
        ).count()
        sessions_attending_in_progress = attending_sessions.filter(
            status=StudySession.STATUS_IN_PROGRESS
        ).count()
        sessions_attending_completed = attending_sessions.filter(
            status=StudySession.STATUS_COMPLETED
        ).count()
        
        # Participation statistics (all participations including hosting)
        all_participations = SessionParticipant.objects.filter(user=self.user)
        
        total_participations = all_participations.count()
        participations_attended = all_participations.filter(
            status=SessionParticipant.STATUS_ATTENDED
        ).count()
        participations_registered = all_participations.filter(
            status=SessionParticipant.STATUS_REGISTERED
        ).count()
        participations_no_show = all_participations.filter(
            status=SessionParticipant.STATUS_NO_SHOW
        ).count()
        participations_cancelled = all_participations.filter(
            status=SessionParticipant.STATUS_CANCELLED
        ).count()
        
        # Session type breakdown (all sessions user is involved in)
        all_user_sessions = StudySession.objects.filter(
            Q(host=self.user) |
            Q(participants__user=self.user)
        ).distinct()
        
        sessions_by_type = {
            'in_person': all_user_sessions.filter(
                session_type=StudySession.TYPE_IN_PERSON
            ).count(),
            'virtual': all_user_sessions.filter(
                session_type=StudySession.TYPE_VIRTUAL
            ).count(),
            'hybrid': all_user_sessions.filter(
                session_type=StudySession.TYPE_HYBRID
            ).count(),
        }
        
        # Total participants across all hosted sessions
        total_participants_in_hosted_sessions = SessionParticipant.objects.filter(
            session__host=self.user,
            status__in=[
                SessionParticipant.STATUS_REGISTERED,
                SessionParticipant.STATUS_ATTENDED
            ]
        ).exclude(user=self.user).count()
        
        return {
            'sessions_hosted_total': sessions_hosted_total,
            'sessions_hosted_upcoming': sessions_hosted_upcoming,
            'sessions_hosted_in_progress': sessions_hosted_in_progress,
            'sessions_hosted_completed': sessions_hosted_completed,
            'sessions_hosted_cancelled': sessions_hosted_cancelled,
            'sessions_attending_total': sessions_attending_total,
            'sessions_attending_upcoming': sessions_attending_upcoming,
            'sessions_attending_in_progress': sessions_attending_in_progress,
            'sessions_attending_completed': sessions_attending_completed,
            'total_participations': total_participations,
            'participations_attended': participations_attended,
            'participations_registered': participations_registered,
            'participations_no_show': participations_no_show,
            'participations_cancelled': participations_cancelled,
            'sessions_by_type': sessions_by_type,
            'total_participants_in_hosted_sessions': total_participants_in_hosted_sessions,
        }

