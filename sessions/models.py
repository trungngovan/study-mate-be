from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from learning.models import Subject


class StudySession(models.Model):
    """
    Model representing a scheduled study session.
    Can be in-person (with location) or virtual (with meeting link).
    """

    # Session Type Choices
    TYPE_IN_PERSON = "in_person"
    TYPE_VIRTUAL = "virtual"
    TYPE_HYBRID = "hybrid"

    TYPE_CHOICES = [
        (TYPE_IN_PERSON, "In Person"),
        (TYPE_VIRTUAL, "Virtual"),
        (TYPE_HYBRID, "Hybrid"),
    ]

    # Recurrence Pattern Choices
    RECURRENCE_NONE = "none"
    RECURRENCE_DAILY = "daily"
    RECURRENCE_WEEKLY = "weekly"
    RECURRENCE_MONTHLY = "monthly"

    RECURRENCE_CHOICES = [
        (RECURRENCE_NONE, "None"),
        (RECURRENCE_DAILY, "Daily"),
        (RECURRENCE_WEEKLY, "Weekly"),
        (RECURRENCE_MONTHLY, "Monthly"),
    ]

    # Status Choices
    STATUS_UPCOMING = "upcoming"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    # Core Fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_sessions')

    # Session Type
    session_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_IN_PERSON)

    # Location (for in-person or hybrid sessions)
    location_name = models.CharField(max_length=255, blank=True, help_text="E.g., Library Room 301")
    location_address = models.TextField(blank=True)
    geom_point = gis_models.PointField(geography=True, null=True, blank=True, srid=4326, help_text="Geographic location of the session")

    # Virtual Meeting Link (for virtual or hybrid sessions)
    meeting_link = models.URLField(blank=True, help_text="Zoom, Google Meet, etc.")

    # Scheduling
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")

    # Recurrence
    recurrence_pattern = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default=RECURRENCE_NONE)
    recurrence_end_date = models.DateField(null=True, blank=True, help_text="When recurrence stops")

    # Capacity
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of participants (null = unlimited)")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_sessions'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['host']),
            models.Index(fields=['session_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate model fields"""
        super().clean()

        # Validate location for in-person sessions
        if self.session_type in [self.TYPE_IN_PERSON, self.TYPE_HYBRID]:
            if not self.location_name and not self.geom_point:
                raise ValidationError("In-person or hybrid sessions must have a location name or geographic point.")

        # Validate meeting link for virtual sessions
        if self.session_type in [self.TYPE_VIRTUAL, self.TYPE_HYBRID]:
            if not self.meeting_link:
                raise ValidationError("Virtual or hybrid sessions must have a meeting link.")

        # Validate recurrence
        if self.recurrence_pattern != self.RECURRENCE_NONE and not self.recurrence_end_date:
            raise ValidationError("Recurring sessions must have a recurrence end date.")

        # Validate duration
        if self.duration_minutes <= 0:
            raise ValidationError("Duration must be greater than 0.")

    @property
    def end_time(self):
        """Calculate end time based on start time and duration"""
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def is_full(self):
        """Check if session has reached max capacity"""
        if self.max_participants is None:
            return False
        return self.participants.filter(status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]).count() >= self.max_participants

    @property
    def participant_count(self):
        """Get current number of registered participants"""
        return self.participants.filter(status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]).count()

    def can_join(self, user):
        """Check if a user can join the session"""
        if self.is_full:
            return False
        if self.status == self.STATUS_CANCELLED:
            return False
        if self.participants.filter(user=user, status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]).exists():
            return False
        return True

    def update_status(self):
        """Auto-update status based on current time"""
        now = timezone.now()

        if self.status == self.STATUS_CANCELLED:
            return  # Don't change cancelled status

        if now < self.start_time:
            self.status = self.STATUS_UPCOMING
        elif now >= self.start_time and now < self.end_time:
            self.status = self.STATUS_IN_PROGRESS
        elif now >= self.end_time:
            self.status = self.STATUS_COMPLETED

        self.save(update_fields=['status', 'updated_at'])


class SessionParticipant(models.Model):
    """
    Model representing a user's participation in a study session.
    Tracks registration, attendance, and check-in/out times.
    """

    # Status Choices
    STATUS_REGISTERED = "registered"
    STATUS_ATTENDED = "attended"
    STATUS_NO_SHOW = "no_show"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_REGISTERED, "Registered"),
        (STATUS_ATTENDED, "Attended"),
        (STATUS_NO_SHOW, "No Show"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    # Core Fields
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_participations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REGISTERED)

    # Attendance Tracking
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True, help_text="Participant's personal notes about the session")

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'session_participants'
        unique_together = [['session', 'user']]
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.session.title}"

    def check_in(self):
        """Mark participant as checked in"""
        if not self.check_in_time:
            self.check_in_time = timezone.now()
            self.status = self.STATUS_ATTENDED
            self.save(update_fields=['check_in_time', 'status', 'updated_at'])

    def check_out(self):
        """Mark participant as checked out"""
        if self.check_in_time and not self.check_out_time:
            self.check_out_time = timezone.now()
            self.save(update_fields=['check_out_time', 'updated_at'])

    @property
    def duration_minutes(self):
        """Calculate time spent in session (if checked in and out)"""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            return int(delta.total_seconds() / 60)
        return None

    def cancel(self):
        """Cancel participation"""
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=['status', 'updated_at'])
