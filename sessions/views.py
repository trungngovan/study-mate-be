"""
Views for sessions app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.utils import timezone
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import StudySession, SessionParticipant
from .serializers import (
    StudySessionListSerializer,
    StudySessionDetailSerializer,
    CreateStudySessionSerializer,
    UpdateStudySessionSerializer,
    SessionParticipantSerializer,
    JoinSessionSerializer,
    CheckInSerializer,
    CheckOutSerializer,
)
from .permissions import IsSessionHost, IsSessionParticipant, CanJoinSession


class StudySessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing study sessions.

    Endpoints:
    - GET /api/sessions/ - List study sessions
    - POST /api/sessions/ - Create a new session
    - GET /api/sessions/{id}/ - Get session details
    - PUT/PATCH /api/sessions/{id}/ - Update session (host only)
    - DELETE /api/sessions/{id}/ - Cancel session (host only)
    - POST /api/sessions/{id}/join/ - Join a session
    - POST /api/sessions/{id}/leave/ - Leave a session
    - POST /api/sessions/{id}/check_in/ - Check in to a session
    - POST /api/sessions/{id}/check_out/ - Check out of a session
    - GET /api/sessions/{id}/participants/ - List participants
    - GET /api/sessions/my_sessions/ - List user's sessions (hosting or attending)
    - GET /api/sessions/monthly_sessions/ - Get user's sessions for a specific month
    - GET /api/sessions/nearby/ - Find nearby sessions
    """

    permission_classes = [IsAuthenticated]
    queryset = StudySession.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return CreateStudySessionSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateStudySessionSerializer
        elif self.action == 'retrieve':
            return StudySessionDetailSerializer
        elif self.action == 'join':
            return JoinSessionSerializer
        elif self.action == 'check_in':
            return CheckInSerializer
        elif self.action == 'check_out':
            return CheckOutSerializer
        return StudySessionListSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSessionHost()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filter and annotate queryset based on query parameters.
        """
        queryset = StudySession.objects.select_related(
            'host', 'subject'
        ).prefetch_related(
            'participants__user'
        )

        # Filter by status
        session_status = self.request.query_params.get('status')
        if session_status:
            queryset = queryset.filter(status=session_status)
        else:
            # By default, exclude cancelled sessions
            queryset = queryset.exclude(status=StudySession.STATUS_CANCELLED)

        # Filter by session type
        session_type = self.request.query_params.get('session_type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)

        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        # Filter by upcoming/past
        time_filter = self.request.query_params.get('time_filter')
        now = timezone.now()
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_time__gte=now)
        elif time_filter == 'past':
            queryset = queryset.filter(start_time__lt=now)

        return queryset.order_by('start_time')

    @extend_schema(
        request=CreateStudySessionSerializer,
        responses={201: StudySessionDetailSerializer},
        description="Create a new study session"
    )
    def create(self, request, *args, **kwargs):
        """Create a new study session."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()

        # Auto-register host as participant
        SessionParticipant.objects.create(
            session=session,
            user=request.user,
            status=SessionParticipant.STATUS_REGISTERED
        )

        response_serializer = StudySessionDetailSerializer(
            session,
            context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={200: StudySessionDetailSerializer},
        description="Get study session details"
    )
    def retrieve(self, request, *args, **kwargs):
        """Get session details."""
        instance = self.get_object()
        instance.update_status()  # Update status before returning
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        description="Delete (cancel) a study session (host only)"
    )
    def destroy(self, request, *args, **kwargs):
        """Cancel a session."""
        instance = self.get_object()
        instance.status = StudySession.STATUS_CANCELLED
        instance.save(update_fields=['status', 'updated_at'])
        return Response(
            {'message': 'Session cancelled successfully.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                enum=['upcoming', 'in_progress', 'completed', 'cancelled'],
                description='Filter by session status'
            ),
            OpenApiParameter(
                name='session_type',
                type=OpenApiTypes.STR,
                enum=['in_person', 'virtual', 'hybrid'],
                description='Filter by session type'
            ),
            OpenApiParameter(
                name='subject',
                type=OpenApiTypes.INT,
                description='Filter by subject ID'
            ),
            OpenApiParameter(
                name='time_filter',
                type=OpenApiTypes.STR,
                enum=['upcoming', 'past'],
                description='Filter by time (upcoming or past)'
            ),
        ],
        responses={200: StudySessionListSerializer(many=True)},
        description="List all study sessions with optional filters"
    )
    def list(self, request, *args, **kwargs):
        """List study sessions."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=JoinSessionSerializer,
        responses={200: SessionParticipantSerializer},
        description="Join a study session"
    )
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a study session."""
        session = self.get_object()

        # Check if can join
        if not session.can_join(request.user):
            return Response(
                {'error': 'Cannot join this session. It may be full, cancelled, or you are already a participant.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = JoinSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create participant
        participant = SessionParticipant.objects.create(
            session=session,
            user=request.user,
            status=SessionParticipant.STATUS_REGISTERED,
            notes=serializer.validated_data.get('notes', '')
        )

        response_serializer = SessionParticipantSerializer(
            participant,
            context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: {'message': 'string'}},
        description="Leave a study session"
    )
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a study session."""
        session = self.get_object()

        # Find participant record
        try:
            participant = session.participants.get(
                user=request.user,
                status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
            )
            participant.cancel()
            return Response(
                {'message': 'You have left the session.'},
                status=status.HTTP_200_OK
            )
        except SessionParticipant.DoesNotExist:
            return Response(
                {'error': 'You are not a participant in this session.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        request=CheckInSerializer,
        responses={200: SessionParticipantSerializer},
        description="Check in to a study session"
    )
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in to a session."""
        session = self.get_object()

        try:
            participant = session.participants.get(
                user=request.user,
                status=SessionParticipant.STATUS_REGISTERED
            )
            participant.check_in()

            response_serializer = SessionParticipantSerializer(
                participant,
                context={'request': request}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except SessionParticipant.DoesNotExist:
            return Response(
                {'error': 'You are not registered for this session or have already checked in.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        request=CheckOutSerializer,
        responses={200: SessionParticipantSerializer},
        description="Check out of a study session"
    )
    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Check out of a session."""
        session = self.get_object()

        try:
            participant = session.participants.get(
                user=request.user,
                status=SessionParticipant.STATUS_ATTENDED
            )

            if not participant.check_in_time:
                return Response(
                    {'error': 'You must check in before checking out.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            participant.check_out()

            response_serializer = SessionParticipantSerializer(
                participant,
                context={'request': request}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except SessionParticipant.DoesNotExist:
            return Response(
                {'error': 'You have not checked in to this session.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                description='Page number for pagination'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description='Number of results per page'
            ),
        ],
        responses={200: SessionParticipantSerializer(many=True)},
        description="List participants of a study session (paginated)"
    )
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """List session participants with pagination."""
        from rest_framework.pagination import PageNumberPagination
        
        session = self.get_object()
        participants = session.participants.select_related('user').order_by('joined_at')

        # Create paginator instance
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 12))
        paginator.max_page_size = 100
        
        # Paginate the queryset
        page = paginator.paginate_queryset(participants, request)
        if page is not None:
            serializer = SessionParticipantSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination is not configured
        serializer = SessionParticipantSerializer(
            participants,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='role',
                type=OpenApiTypes.STR,
                enum=['hosting', 'attending'],
                description='Filter by user role (hosting or attending)'
            ),
        ],
        responses={200: StudySessionListSerializer(many=True)},
        description="List sessions the current user is hosting or attending"
    )
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """List user's sessions (hosting or attending)."""
        user = request.user
        role = request.query_params.get('role')

        if role == 'hosting':
            queryset = StudySession.objects.filter(host=user)
        elif role == 'attending':
            queryset = StudySession.objects.filter(
                participants__user=user,
                participants__status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
            ).exclude(host=user)
        else:
            # Both hosting and attending
            queryset = StudySession.objects.filter(
                models.Q(host=user) |
                models.Q(
                    participants__user=user,
                    participants__status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
                )
            ).distinct()

        queryset = queryset.select_related('host', 'subject').order_by('start_time')

        # Exclude cancelled by default
        queryset = queryset.exclude(status=StudySession.STATUS_CANCELLED)

        serializer = StudySessionListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='month',
                type=OpenApiTypes.INT,
                description='Month (1-12)',
                required=True
            ),
            OpenApiParameter(
                name='year',
                type=OpenApiTypes.INT,
                description='Year (e.g., 2024)',
                required=True
            ),
        ],
        responses={200: StudySessionListSerializer(many=True)},
        description="Get all user sessions within a specific month for calendar view. Accepts month and year as query parameters."
    )
    @action(detail=False, methods=['get'], url_path='monthly_sessions')
    def monthly_sessions(self, request):
        """Get all user sessions within a specific month."""
        from datetime import datetime
        from calendar import monthrange
        
        user = request.user
        
        # Get month and year from query params
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response(
                {'error': 'Both month and year are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            month = int(month)
            year = int(year)
            
            # Validate month range
            if month < 1 or month > 12:
                return Response(
                    {'error': 'Month must be between 1 and 12.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate the start and end of the month
            first_day = datetime(year, month, 1, 0, 0, 0)
            last_day_num = monthrange(year, month)[1]
            last_day = datetime(year, month, last_day_num, 23, 59, 59)
            
            # Convert to timezone-aware datetimes using UTC
            first_day = timezone.make_aware(first_day, timezone.get_current_timezone())
            last_day = timezone.make_aware(last_day, timezone.get_current_timezone())
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Month and year must be valid integers.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all sessions for the user (hosting or participating) within the month
        queryset = StudySession.objects.filter(
            models.Q(host=user) |
            models.Q(
                participants__user=user,
                participants__status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
            )
        ).filter(
            start_time__gte=first_day,
            start_time__lte=last_day
        ).distinct().select_related(
            'host', 'subject'
        ).order_by('start_time')
        
        # Exclude cancelled sessions by default
        queryset = queryset.exclude(status=StudySession.STATUS_CANCELLED)
        
        serializer = StudySessionListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='radius_km',
                type=OpenApiTypes.FLOAT,
                description='Search radius in kilometers (default: 5km)'
            ),
            OpenApiParameter(
                name='session_type',
                type=OpenApiTypes.STR,
                enum=['in_person', 'virtual', 'hybrid'],
                description='Filter by session type'
            ),
        ],
        responses={200: StudySessionListSerializer(many=True)},
        description="Find nearby in-person study sessions"
    )
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearby in-person study sessions."""
        user = request.user

        if not user.geom_last_point:
            return Response(
                {'error': 'You must set your location first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get radius from query params (default 5km)
        radius_km = float(request.query_params.get('radius_km', 5))

        # Filter sessions with location
        queryset = StudySession.objects.filter(
            geom_point__isnull=False,
            session_type__in=[StudySession.TYPE_IN_PERSON, StudySession.TYPE_HYBRID],
            status=StudySession.STATUS_UPCOMING,
            start_time__gte=timezone.now()
        ).filter(
            geom_point__dwithin=(user.geom_last_point, D(km=radius_km))
        ).annotate(
            distance_km=Distance('geom_point', user.geom_last_point)
        ).select_related('host', 'subject').order_by('distance_km', 'start_time')

        # Apply session type filter if provided
        session_type = request.query_params.get('session_type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)

        serializer = StudySessionListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
