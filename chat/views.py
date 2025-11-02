from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch, Count
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.models import Conversation, Message
from chat.serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageListSerializer,
    MarkAsReadSerializer,
)
from chat.permissions import IsConversationParticipant, CanMessageConnection
from chat.services import ConversationService
from matching.models import Connection


class MessagePagination(PageNumberPagination):
    """
    Custom pagination for chat messages.
    Optimized for chat UX with larger page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing conversations.
    
    Endpoints:
    - GET /api/chat/conversations/ - List all conversations for current user
    - GET /api/chat/conversations/{id}/ - Get conversation details
    - GET /api/chat/conversations/{id}/messages/ - Get messages in conversation
    - POST /api/chat/conversations/{id}/mark_read/ - Mark messages as read
    """
    
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'messages':
            return MessageListSerializer
        elif self.action == 'mark_read':
            return MarkAsReadSerializer
        return ConversationSerializer
    
    @property
    def paginator(self):
        """
        Use custom pagination for messages endpoint.
        """
        if self.action == 'messages':
            if not hasattr(self, '_messages_paginator'):
                self._messages_paginator = MessagePagination()
            return self._messages_paginator
        return super().paginator
    
    def get_queryset(self):
        """
        Return conversations where the user is a participant.
        Optimized with select_related.
        """
        user = self.request.user
        
        queryset = Conversation.objects.filter(
            Q(connection__user1=user) | Q(connection__user2=user)
        ).select_related(
            'connection',
            'connection__user1',
            'connection__user2',
            'connection__connection_request'
        ).order_by('-last_message_at', '-created_at')
        
        return queryset
    
    @extend_schema(
        summary="List conversations",
        description="Get a list of all conversations for the authenticated user",
        responses={200: ConversationListSerializer(many=True)},
        tags=["Chat"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get conversation details",
        description="Retrieve detailed information about a specific conversation",
        responses={200: ConversationSerializer},
        tags=["Chat"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get or create conversation by connection ID",
        description="Get conversation for a connection. Auto-creates if doesn't exist for accepted connections.",
        parameters=[
            OpenApiParameter(
                name='connection_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Connection ID',
                required=True
            ),
        ],
        responses={200: ConversationSerializer},
        tags=["Chat"]
    )
    @action(detail=False, methods=['get'], url_path='by-connection')
    def by_connection(self, request):
        """
        Get or create conversation by connection ID.
        Auto-creates conversation if it doesn't exist for accepted connections.
        """
        connection_id = request.query_params.get('connection_id')
        
        if not connection_id:
            return Response(
                {'error': 'connection_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get connection and verify user is a participant
            connection = Connection.objects.select_related(
                'user1', 'user2', 'connection_request'
            ).get(id=connection_id)
            
            # Check if user is a participant
            user = request.user
            if connection.user1 != user and connection.user2 != user:
                return Response(
                    {'error': 'You are not a participant in this connection'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if connection is accepted
            if not connection.connection_request or not connection.connection_request.can_message():
                return Response(
                    {'error': 'Connection must be accepted to create conversation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create conversation
            conversation = ConversationService.get_or_create_conversation(connection)
            
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
            
        except Connection.DoesNotExist:
            return Response(
                {'error': 'Connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Get conversation messages",
        description=(
            "Retrieve paginated messages for a specific conversation.\n\n"
            "**Ordering**: Messages are ordered by `created_at` DESC (newest first).\n\n"
            "**Pagination Flow**:\n"
            "- `page=1`: Returns the newest messages (most recent messages)\n"
            "- `next`: Returns older messages (scroll up to see older messages)\n"
            "- `previous`: Returns newer messages (scroll down to see newer messages)\n\n"
            "**Default page_size**: 10 messages per page (max: 10)\n\n"
            "For real-time updates, use WebSocket connection to receive new messages instantly."
        ),
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number for pagination (default: 1)'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of messages per page (default: 10, max: 10)'
            ),
        ],
        responses={200: MessageListSerializer(many=True)},
        tags=["Chat"]
    )
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages in a conversation with pagination.
        
        Messages are ordered chronologically (newest first) for optimal chat UX.
        Use 'next' link to load older messages, 'previous' for newer messages.
        """
        conversation = self.get_object()
        
        # Get messages ordered by creation time (newest first for chat UX)
        messages = conversation.messages.select_related(
            'sender'
        ).order_by('-created_at')
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mark messages as read",
        description="Mark one or more messages as read in a conversation",
        request=MarkAsReadSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'marked_count': {'type': 'integer'},
                }
            }
        },
        tags=["Chat"]
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark messages as read in a conversation."""
        conversation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_ids = serializer.validated_data.get('message_ids')
        user = request.user
        
        # Get unread messages (not sent by current user)
        unread_messages = conversation.messages.filter(
            read_at__isnull=True
        ).exclude(sender=user)
        
        # If specific message IDs provided, filter by them
        if message_ids:
            unread_messages = unread_messages.filter(id__in=message_ids)
        
        # Get list of message IDs before updating
        marked_message_ids = list(unread_messages.values_list('id', flat=True))
        
        # Mark as read
        read_at = timezone.now()
        marked_count = unread_messages.update(read_at=read_at)
        
        # Broadcast read receipts to WebSocket channel
        if marked_count > 0:
            channel_layer = get_channel_layer()
            room_group_name = f'chat_{conversation.id}'
            
            try:
                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'messages_read',
                        'user_id': user.id,
                        'message_ids': marked_message_ids,
                        'read_at': read_at.isoformat(),
                    }
                )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Error broadcasting read receipt to WebSocket: {e}")
        
        return Response({
            'message': f'Marked {marked_count} message(s) as read',
            'marked_count': marked_count
        })


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    
    Endpoints:
    - POST /api/chat/messages/ - Send a new message
    - GET /api/chat/messages/{id}/ - Get message details
    """
    
    permission_classes = [IsAuthenticated, CanMessageConnection, IsConversationParticipant]
    
    def get_serializer_class(self):
        """Use different serializers for create and other actions."""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """
        Return messages from conversations where the user is a participant.
        """
        user = self.request.user
        
        return Message.objects.filter(
            Q(conversation__connection__user1=user) | 
            Q(conversation__connection__user2=user)
        ).select_related(
            'sender',
            'conversation',
            'conversation__connection'
        ).order_by('-created_at')
    
    @extend_schema(
        summary="Send a message",
        description="Send a new message in a conversation",
        request=MessageCreateSerializer,
        responses={201: MessageSerializer},
        tags=["Chat"]
    )
    def create(self, request, *args, **kwargs):
        """Create a new message and broadcast to WebSocket."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # Broadcast message to WebSocket channel
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{message.conversation.id}'
        
        try:
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender_id': message.sender.id,
                    'sender_name': message.sender.full_name,
                    'sender_avatar': message.sender.avatar_url,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                }
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error broadcasting message to WebSocket: {e}")
        
        # Return full message details
        output_serializer = MessageSerializer(message, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get message details",
        description="Retrieve detailed information about a specific message",
        responses={200: MessageSerializer},
        tags=["Chat"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # Disable update and delete for messages
    def update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Messages cannot be updated'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Messages cannot be updated'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        return Response(
            {'error': 'Messages cannot be deleted'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

