from django.contrib import admin
from .models import StudySession, SessionParticipant


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    """Admin interface for StudySession model."""

    list_display = [
        'id',
        'title',
        'host',
        'session_type',
        'start_time',
        'duration_minutes',
        'participant_count',
        'status',
        'created_at',
    ]

    list_filter = [
        'session_type',
        'status',
        'recurrence_pattern',
        'start_time',
        'created_at',
    ]

    search_fields = [
        'title',
        'description',
        'host__email',
        'host__full_name',
        'location_name',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'participant_count',
        'is_full',
        'end_time',
    ]

    list_per_page = 25

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'host', 'subject', 'status')
        }),
        ('Session Type & Location', {
            'fields': (
                'session_type',
                'location_name',
                'location_address',
                'geom_point',
                'meeting_link',
            )
        }),
        ('Scheduling', {
            'fields': (
                'start_time',
                'duration_minutes',
                'recurrence_pattern',
                'recurrence_end_date',
            )
        }),
        ('Capacity', {
            'fields': ('max_participants', 'participant_count', 'is_full')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'end_time')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('host', 'subject')


@admin.register(SessionParticipant)
class SessionParticipantAdmin(admin.ModelAdmin):
    """Admin interface for SessionParticipant model."""

    list_display = [
        'id',
        'user',
        'session',
        'status',
        'check_in_time',
        'check_out_time',
        'duration_minutes',
        'joined_at',
    ]

    list_filter = [
        'status',
        'check_in_time',
        'joined_at',
    ]

    search_fields = [
        'user__email',
        'user__full_name',
        'session__title',
    ]

    readonly_fields = [
        'joined_at',
        'updated_at',
        'duration_minutes',
    ]

    list_per_page = 25

    fieldsets = (
        ('Participation Info', {
            'fields': ('session', 'user', 'status', 'notes')
        }),
        ('Attendance', {
            'fields': ('check_in_time', 'check_out_time', 'duration_minutes')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('session', 'user')
