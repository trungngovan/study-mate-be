"""
Views for matching app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import ConnectionRequest
from .serializers import (
    ConnectionRequestSerializer,
    SendConnectionRequestSerializer,
    AcceptConnectionRequestSerializer,
    RejectConnectionRequestSerializer,
    ConnectionRequestListSerializer,
    ConnectionStatusSerializer,
    ConnectionStatisticsSerializer,
    AcceptedConnectionSerializer,
)
from .services import ConnectionService
from . import schema


User = get_user_model()


class ConnectionRequestViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing connection requests.
    
    Endpoints:
    - POST /api/matching/requests/ - Send a connection request
    - GET /api/matching/requests/ - List all connection requests
    - GET /api/matching/requests/{id}/ - Get connection request detail
    - POST /api/matching/requests/{id}/accept/ - Accept a request
    - POST /api/matching/requests/{id}/reject/ - Reject a request
    - POST /api/matching/requests/{id}/block/ - Block a connection
    - GET /api/matching/requests/sent/ - List sent requests
    - GET /api/matching/requests/received/ - List received requests
    - GET /api/matching/requests/pending/ - List all pending requests
    """
    
    permission_classes = [IsAuthenticated]
    queryset = ConnectionRequest.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return SendConnectionRequestSerializer
        elif self.action == 'accept':
            return AcceptConnectionRequestSerializer
        elif self.action == 'reject':
            return RejectConnectionRequestSerializer
        elif self.action in ['list', 'sent', 'received', 'pending']:
            return ConnectionRequestListSerializer
        return ConnectionRequestSerializer
    
    def get_queryset(self):
        """Filter queryset based on current user."""
        user = self.request.user
        return ConnectionRequest.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        ).select_related('sender', 'receiver').order_by('-created_at')
    
    @extend_schema(
        request=SendConnectionRequestSerializer,
        responses={201: ConnectionRequestSerializer},
        **schema.SEND_CONNECTION_REQUEST_SCHEMA
    )
    def create(self, request):
        """Send a connection request to another user."""
        serializer = SendConnectionRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        receiver = get_object_or_404(User, id=serializer.validated_data['receiver_id'])
        message = serializer.validated_data.get('message', '')
        
        # Use service to send request
        connection_request = ConnectionService.send_connection_request(
            sender=request.user,
            receiver=receiver,
            message=message
        )
        
        response_serializer = ConnectionRequestSerializer(
            connection_request,
            context={'request': request}
        )
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        responses={200: ConnectionRequestSerializer},
        **schema.GET_CONNECTION_REQUEST_SCHEMA
    )
    def retrieve(self, request, pk=None):
        """Get details of a specific connection request."""
        connection_request = get_object_or_404(
            ConnectionRequest,
            pk=pk
        )
        
        # Check permission - only sender or receiver can view
        if connection_request.sender != request.user and connection_request.receiver != request.user:
            return Response(
                {'detail': 'You do not have permission to view this connection request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ConnectionRequestSerializer(
            connection_request,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ConnectionRequestListSerializer(many=True)},
        **schema.LIST_CONNECTION_REQUESTS_SCHEMA
    )
    def list(self, request):
        """List all connection requests (sent and received)."""
        queryset = self.get_queryset()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ConnectionRequestListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        # Non-paginated fallback
        serializer = ConnectionRequestListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        request=AcceptConnectionRequestSerializer,
        responses={200: ConnectionRequestSerializer},
        **schema.ACCEPT_CONNECTION_REQUEST_SCHEMA
    )
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a connection request."""
        connection_request = get_object_or_404(ConnectionRequest, pk=pk)
        
        # Only receiver can accept
        if connection_request.receiver != request.user:
            return Response(
                {'detail': 'Only the receiver can accept this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if request is in pending state
        if connection_request.state != ConnectionRequest.STATE_PENDING:
            return Response(
                {'detail': f'Cannot accept request in {connection_request.state} state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accept the request (creates Connection immediately)
        connection_request = ConnectionService.accept_connection_request(
            connection_request
        )
        
        serializer = ConnectionRequestSerializer(
            connection_request,
            context={'request': request}
        )
        
        return Response(serializer.data)
    
    @extend_schema(
        request=RejectConnectionRequestSerializer,
        responses={200: ConnectionRequestSerializer},
        **schema.REJECT_CONNECTION_REQUEST_SCHEMA
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a connection request."""
        connection_request = get_object_or_404(ConnectionRequest, pk=pk)
        
        # Only receiver can reject
        if connection_request.receiver != request.user:
            return Response(
                {'detail': 'Only the receiver can reject this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if request is in pending state
        if connection_request.state != ConnectionRequest.STATE_PENDING:
            return Response(
                {'detail': f'Cannot reject request in {connection_request.state} state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reject the request
        connection_request = ConnectionService.reject_connection_request(
            connection_request
        )
        
        serializer = ConnectionRequestSerializer(
            connection_request,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ConnectionRequestSerializer},
        **schema.BLOCK_CONNECTION_SCHEMA
    )
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a connection."""
        connection_request = get_object_or_404(ConnectionRequest, pk=pk)
        
        # Only participants can block
        if connection_request.sender != request.user and connection_request.receiver != request.user:
            return Response(
                {'detail': 'Only participants can block this connection'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Block the connection
        connection_request = ConnectionService.block_connection(connection_request)
        
        serializer = ConnectionRequestSerializer(
            connection_request,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={204: None},
        description='Cancel a sent connection request',
        summary='Cancel/delete a sent connection request',
        tags=['Matching - Requests']
    )
    def destroy(self, request, pk=None):
        """
        Cancel/delete a sent connection request.
        Only the sender can cancel their own pending requests.
        """
        connection_request = get_object_or_404(ConnectionRequest, pk=pk)
        
        # Only sender can cancel their own request
        if connection_request.sender != request.user:
            return Response(
                {'detail': 'Only the sender can cancel this request'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only pending requests can be canceled
        if connection_request.state != ConnectionRequest.STATE_PENDING:
            return Response(
                {'detail': f'Cannot cancel request in {connection_request.state} state. Only pending requests can be canceled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the request using the service
        ConnectionService.cancel_connection_request(connection_request)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        responses={200: ConnectionRequestListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='state',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by state (pending, accepted, rejected, blocked)',
                required=False
            )
        ],
        **schema.LIST_SENT_REQUESTS_SCHEMA
    )
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """List connection requests sent by current user."""
        state = request.query_params.get('state')
        requests = ConnectionService.get_sent_requests(
            request.user,
            state=state,
            use_cache=False  # Disable cache for pagination support
        )
        
        # Apply pagination
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = ConnectionRequestListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        # Non-paginated fallback
        serializer = ConnectionRequestListSerializer(
            requests,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ConnectionRequestListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='state',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by state (pending, accepted, rejected, blocked)',
                required=False
            )
        ],
        **schema.LIST_RECEIVED_REQUESTS_SCHEMA
    )
    @action(detail=False, methods=['get'])
    def received(self, request):
        """List connection requests received by current user."""
        state = request.query_params.get('state')
        requests = ConnectionService.get_received_requests(
            request.user,
            state=state,
            use_cache=False  # Disable cache for pagination support
        )
        
        # Apply pagination
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = ConnectionRequestListSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        # Non-paginated fallback
        serializer = ConnectionRequestListSerializer(
            requests,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: dict},
        **schema.LIST_PENDING_REQUESTS_SCHEMA
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """List all pending requests (both sent and received)."""
        pending_requests = ConnectionService.get_pending_requests(request.user)
        
        return Response({
            'sent': ConnectionRequestListSerializer(
                pending_requests['sent'],
                many=True,
                context={'request': request}
            ).data,
            'received': ConnectionRequestListSerializer(
                pending_requests['received'],
                many=True,
                context={'request': request}
            ).data
        })


class ConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing accepted connections.
    
    Endpoints:
    - GET /api/matching/connections/ - List accepted connections
    - GET /api/matching/connections/{id}/ - Get connection detail
    - GET /api/matching/connections/statistics/ - Get connection statistics
    - GET /api/matching/connections/status/{user_id}/ - Check connection status with user
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = AcceptedConnectionSerializer
    
    def get_queryset(self):
        """Get accepted connections for current user."""
        return ConnectionService.get_accepted_connections(
            self.request.user,
            use_cache=False  # Disable cache for pagination support
        )
    
    @extend_schema(
        responses={200: AcceptedConnectionSerializer(many=True)},
        **schema.LIST_CONNECTIONS_SCHEMA
    )
    def list(self, request):
        """List all accepted connections for current user."""
        connections = self.get_queryset()
        
        # Apply pagination
        page = self.paginate_queryset(connections)
        if page is not None:
            serializer = AcceptedConnectionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        # Non-paginated fallback
        serializer = AcceptedConnectionSerializer(
            connections,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: AcceptedConnectionSerializer},
        **schema.GET_CONNECTION_SCHEMA
    )
    def retrieve(self, request, pk=None):
        """Get details of a specific connection."""
        # Get the connection request
        connection_request = get_object_or_404(
            ConnectionRequest,
            pk=pk,
            state=ConnectionRequest.STATE_ACCEPTED
        )
        
        # Check permission - user must be sender or receiver
        if connection_request.sender != request.user and connection_request.receiver != request.user:
            return Response(
                {'detail': 'You do not have permission to view this connection'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AcceptedConnectionSerializer(
            connection_request,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ConnectionStatisticsSerializer},
        **schema.CONNECTION_STATISTICS_SCHEMA
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get connection statistics for current user."""
        stats = ConnectionService.get_connection_statistics(request.user)
        
        serializer = ConnectionStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ConnectionStatusSerializer},
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID of the user to check connection status with',
                required=True
            )
        ],
        **schema.CONNECTION_STATUS_SCHEMA
    )
    @action(detail=False, methods=['get'], url_path='status/(?P<user_id>[^/.]+)')
    def status(self, request, user_id=None):
        """Check connection status with another user."""
        other_user = get_object_or_404(User, pk=user_id)
        
        status_data = ConnectionService.get_connection_status(
            request.user,
            other_user
        )
        
        serializer = ConnectionStatusSerializer(status_data)
        return Response(serializer.data)
