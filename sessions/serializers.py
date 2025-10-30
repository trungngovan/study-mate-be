"""
Serializers for sessions app.
"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from .models import StudySession, SessionParticipant
from learning.models import Subject


User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for sessions."""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'avatar_url',
            'school',
            'major',
            'year',
        ]
        read_only_fields = fields


class SubjectBasicSerializer(serializers.ModelSerializer):
    """Basic subject information."""

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name_en', 'name_vi', 'level']
        read_only_fields = fields


class SessionParticipantSerializer(serializers.ModelSerializer):
    """Serializer for session participant details."""

    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = SessionParticipant
        fields = [
            'id',
            'user',
            'status',
            'check_in_time',
            'check_out_time',
            'duration_minutes',
            'notes',
            'joined_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'check_in_time',
            'check_out_time',
            'duration_minutes',
            'joined_at',
            'updated_at',
        ]


class StudySessionListSerializer(serializers.ModelSerializer):
    """Serializer for study session list view (lightweight)."""

    host = UserBasicSerializer(read_only=True)
    subject = SubjectBasicSerializer(read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)
    is_host = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = StudySession
        fields = [
            'id',
            'title',
            'description',
            'host',
            'subject',
            'session_type',
            'location_name',
            'start_time',
            'end_time',
            'duration_minutes',
            'participant_count',
            'max_participants',
            'is_full',
            'status',
            'is_host',
            'is_participant',
            'created_at',
        ]
        read_only_fields = fields

    def get_is_host(self, obj):
        """Check if current user is the host."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.host == request.user
        return False

    def get_is_participant(self, obj):
        """Check if current user is a participant."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(
                user=request.user,
                status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
            ).exists()
        return False


class StudySessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for study session detail view (complete)."""

    host = UserBasicSerializer(read_only=True)
    subject = SubjectBasicSerializer(read_only=True)
    participants = SessionParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)
    is_host = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = StudySession
        fields = [
            'id',
            'title',
            'description',
            'host',
            'subject',
            'session_type',
            'location_name',
            'location_address',
            'geom_point',
            'meeting_link',
            'start_time',
            'end_time',
            'duration_minutes',
            'recurrence_pattern',
            'recurrence_end_date',
            'max_participants',
            'participant_count',
            'is_full',
            'status',
            'participants',
            'is_host',
            'is_participant',
            'can_join',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'host',
            'participant_count',
            'is_full',
            'end_time',
            'status',
            'participants',
            'is_host',
            'is_participant',
            'can_join',
            'created_at',
            'updated_at',
        ]

    def get_is_host(self, obj):
        """Check if current user is the host."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.host == request.user
        return False

    def get_is_participant(self, obj):
        """Check if current user is a participant."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(
                user=request.user,
                status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
            ).exists()
        return False

    def get_can_join(self, obj):
        """Check if current user can join the session."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_join(request.user)
        return False


class CreateStudySessionSerializer(serializers.ModelSerializer):
    """Serializer for creating a study session."""

    # Optional: accept latitude/longitude for creating geom_point
    latitude = serializers.FloatField(required=False, write_only=True)
    longitude = serializers.FloatField(required=False, write_only=True)

    class Meta:
        model = StudySession
        fields = [
            'title',
            'description',
            'subject',
            'session_type',
            'location_name',
            'location_address',
            'latitude',
            'longitude',
            'meeting_link',
            'start_time',
            'duration_minutes',
            'recurrence_pattern',
            'recurrence_end_date',
            'max_participants',
        ]

    def validate(self, data):
        """Validate session data."""
        session_type = data.get('session_type')

        # Validate location for in-person sessions
        if session_type in [StudySession.TYPE_IN_PERSON, StudySession.TYPE_HYBRID]:
            if not data.get('location_name') and not (data.get('latitude') and data.get('longitude')):
                raise serializers.ValidationError(
                    "In-person or hybrid sessions must have a location name or coordinates."
                )

        # Validate meeting link for virtual sessions
        if session_type in [StudySession.TYPE_VIRTUAL, StudySession.TYPE_HYBRID]:
            if not data.get('meeting_link'):
                raise serializers.ValidationError(
                    "Virtual or hybrid sessions must have a meeting link."
                )

        # Validate recurrence
        if data.get('recurrence_pattern') != StudySession.RECURRENCE_NONE:
            if not data.get('recurrence_end_date'):
                raise serializers.ValidationError(
                    "Recurring sessions must have a recurrence end date."
                )

        return data

    def create(self, validated_data):
        """Create session with host set to current user."""
        # Extract latitude/longitude if provided
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        # Set the host to the current user
        validated_data['host'] = self.context['request'].user

        # Create geom_point if coordinates provided
        if latitude is not None and longitude is not None:
            validated_data['geom_point'] = Point(longitude, latitude, srid=4326)

        return super().create(validated_data)


class UpdateStudySessionSerializer(serializers.ModelSerializer):
    """Serializer for updating a study session (host only)."""

    latitude = serializers.FloatField(required=False, write_only=True)
    longitude = serializers.FloatField(required=False, write_only=True)

    class Meta:
        model = StudySession
        fields = [
            'title',
            'description',
            'subject',
            'session_type',
            'location_name',
            'location_address',
            'latitude',
            'longitude',
            'meeting_link',
            'start_time',
            'duration_minutes',
            'recurrence_pattern',
            'recurrence_end_date',
            'max_participants',
            'status',
        ]

    def validate(self, data):
        """Validate session data."""
        session_type = data.get('session_type', self.instance.session_type)

        # Validate location for in-person sessions
        if session_type in [StudySession.TYPE_IN_PERSON, StudySession.TYPE_HYBRID]:
            location_name = data.get('location_name', self.instance.location_name)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            has_geom = self.instance.geom_point is not None

            if not location_name and not (latitude and longitude) and not has_geom:
                raise serializers.ValidationError(
                    "In-person or hybrid sessions must have a location name or coordinates."
                )

        # Validate meeting link for virtual sessions
        if session_type in [StudySession.TYPE_VIRTUAL, StudySession.TYPE_HYBRID]:
            meeting_link = data.get('meeting_link', self.instance.meeting_link)
            if not meeting_link:
                raise serializers.ValidationError(
                    "Virtual or hybrid sessions must have a meeting link."
                )

        return data

    def update(self, instance, validated_data):
        """Update session with optional coordinate update."""
        # Extract and handle coordinates
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        if latitude is not None and longitude is not None:
            validated_data['geom_point'] = Point(longitude, latitude, srid=4326)

        return super().update(instance, validated_data)


class JoinSessionSerializer(serializers.Serializer):
    """Serializer for joining a session."""

    notes = serializers.CharField(required=False, allow_blank=True)


class CheckInSerializer(serializers.Serializer):
    """Serializer for checking in to a session."""
    pass  # No fields needed, just triggers check-in


class CheckOutSerializer(serializers.Serializer):
    """Serializer for checking out of a session."""
    pass  # No fields needed, just triggers check-out
