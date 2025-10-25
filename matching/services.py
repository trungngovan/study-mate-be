"""
Service layer for matching app with Redis caching.
"""
from django.core.cache import cache
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from typing import List, Optional, Dict, Any
import json

from .models import ConnectionRequest, Connection


class ConnectionCacheService:
    """Service for caching connection request data in Redis."""
    
    # Cache key prefixes
    SENT_REQUESTS_KEY = "user:{user_id}:sent_requests"
    RECEIVED_REQUESTS_KEY = "user:{user_id}:received_requests"
    ACCEPTED_CONNECTIONS_KEY = "user:{user_id}:accepted_connections"
    CONNECTION_DETAIL_KEY = "connection_request:{request_id}"
    USER_CONNECTION_COUNT_KEY = "user:{user_id}:connection_count"
    
    @classmethod
    def _get_cache_timeout(cls, key_type: str) -> int:
        """Get cache timeout for specific key type."""
        cache_ttl = getattr(settings, 'CACHE_TTL', {})
        return cache_ttl.get(key_type, 300)
    
    @classmethod
    def get_sent_requests(cls, user_id: int) -> Optional[List[Dict]]:
        """Get cached sent requests for a user."""
        key = cls.SENT_REQUESTS_KEY.format(user_id=user_id)
        cached_data = cache.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    @classmethod
    def set_sent_requests(cls, user_id: int, requests: List[Dict]) -> None:
        """Cache sent requests for a user."""
        key = cls.SENT_REQUESTS_KEY.format(user_id=user_id)
        timeout = cls._get_cache_timeout('CONNECTION_REQUESTS')
        cache.set(key, json.dumps(requests), timeout)
    
    @classmethod
    def get_received_requests(cls, user_id: int) -> Optional[List[Dict]]:
        """Get cached received requests for a user."""
        key = cls.RECEIVED_REQUESTS_KEY.format(user_id=user_id)
        cached_data = cache.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    @classmethod
    def set_received_requests(cls, user_id: int, requests: List[Dict]) -> None:
        """Cache received requests for a user."""
        key = cls.RECEIVED_REQUESTS_KEY.format(user_id=user_id)
        timeout = cls._get_cache_timeout('CONNECTION_REQUESTS')
        cache.set(key, json.dumps(requests), timeout)
    
    @classmethod
    def get_accepted_connections(cls, user_id: int) -> Optional[List[Dict]]:
        """Get cached accepted connections for a user."""
        key = cls.ACCEPTED_CONNECTIONS_KEY.format(user_id=user_id)
        cached_data = cache.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    @classmethod
    def set_accepted_connections(cls, user_id: int, connections: List[Dict]) -> None:
        """Cache accepted connections for a user."""
        key = cls.ACCEPTED_CONNECTIONS_KEY.format(user_id=user_id)
        timeout = cls._get_cache_timeout('ACCEPTED_CONNECTIONS')
        cache.set(key, json.dumps(connections), timeout)
    
    @classmethod
    def get_connection_request(cls, request_id: int) -> Optional[Dict]:
        """Get cached connection request detail."""
        key = cls.CONNECTION_DETAIL_KEY.format(request_id=request_id)
        cached_data = cache.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    @classmethod
    def set_connection_request(cls, request_id: int, request_data: Dict) -> None:
        """Cache connection request detail."""
        key = cls.CONNECTION_DETAIL_KEY.format(request_id=request_id)
        timeout = cls._get_cache_timeout('CONNECTION_REQUESTS')
        cache.set(key, json.dumps(request_data), timeout)
    
    @classmethod
    def invalidate_user_caches(cls, *user_ids: int) -> None:
        """Invalidate all caches for given users."""
        keys_to_delete = []
        
        for user_id in user_ids:
            keys_to_delete.extend([
                cls.SENT_REQUESTS_KEY.format(user_id=user_id),
                cls.RECEIVED_REQUESTS_KEY.format(user_id=user_id),
                cls.ACCEPTED_CONNECTIONS_KEY.format(user_id=user_id),
                cls.USER_CONNECTION_COUNT_KEY.format(user_id=user_id),
            ])
        
        cache.delete_many(keys_to_delete)
    
    @classmethod
    def invalidate_connection_request(cls, request_id: int) -> None:
        """Invalidate cache for a specific connection request."""
        key = cls.CONNECTION_DETAIL_KEY.format(request_id=request_id)
        cache.delete(key)
    
    @classmethod
    def get_connection_count(cls, user_id: int) -> Optional[int]:
        """Get cached connection count for a user."""
        key = cls.USER_CONNECTION_COUNT_KEY.format(user_id=user_id)
        return cache.get(key)
    
    @classmethod
    def set_connection_count(cls, user_id: int, count: int) -> None:
        """Cache connection count for a user."""
        key = cls.USER_CONNECTION_COUNT_KEY.format(user_id=user_id)
        timeout = cls._get_cache_timeout('ACCEPTED_CONNECTIONS')
        cache.set(key, count, timeout)


class ConnectionService:
    """Business logic for managing connections between users."""
    
    @classmethod
    def send_connection_request(cls, sender, receiver, message: str = "") -> ConnectionRequest:
        """
        Send a connection request from sender to receiver.
        """
        # Check if request already exists
        existing = ConnectionRequest.objects.filter(
            sender=sender,
            receiver=receiver
        ).first()
        
        if existing:
            if existing.state == ConnectionRequest.STATE_REJECTED:
                # Allow resending after rejection
                existing.state = ConnectionRequest.STATE_PENDING
                existing.message = message
                existing.save()
                
                # Invalidate caches
                ConnectionCacheService.invalidate_user_caches(sender.id, receiver.id)
                
                return existing
            else:
                # Request already exists and is not rejected
                return existing
        
        # Create new request
        request = ConnectionRequest.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            state=ConnectionRequest.STATE_PENDING
        )
        
        # Invalidate caches
        ConnectionCacheService.invalidate_user_caches(sender.id, receiver.id)
        
        return request
    
    @classmethod
    @transaction.atomic
    def accept_connection_request(cls, request: ConnectionRequest) -> ConnectionRequest:
        """
        Accept a connection request and create Connection immediately.
        Also creates a Conversation for chat.
        Returns the accepted request.
        """
        # Accept the request
        request.accept()
        request.save()
        
        # Create Connection immediately (bidirectional)
        connection, created = Connection.create_from_request(request)
        
        # Create Conversation for chat (always create, even if connection already exists)
        from chat.services import ConversationService
        ConversationService.get_or_create_conversation(connection)
        
        # Invalidate caches for both users
        ConnectionCacheService.invalidate_user_caches(
            request.sender.id,
            request.receiver.id
        )
        
        return request
    
    @classmethod
    def reject_connection_request(cls, request: ConnectionRequest) -> ConnectionRequest:
        """Reject a connection request."""
        request.reject()
        request.save()
        
        # Invalidate caches
        ConnectionCacheService.invalidate_user_caches(
            request.sender.id,
            request.receiver.id
        )
        
        return request
    
    @classmethod
    def block_connection(cls, request: ConnectionRequest) -> ConnectionRequest:
        """Block a connection."""
        request.block()
        request.save()
        
        # Invalidate caches
        ConnectionCacheService.invalidate_user_caches(
            request.sender.id,
            request.receiver.id
        )
        
        return request
    
    @classmethod
    def cancel_connection_request(cls, request: ConnectionRequest) -> None:
        """
        Cancel (delete) a connection request.
        Should only be called for pending requests by the sender.
        """
        sender_id = request.sender.id
        receiver_id = request.receiver.id
        
        # Delete the request
        request.delete()
        
        # Invalidate caches for both users
        ConnectionCacheService.invalidate_user_caches(sender_id, receiver_id)
    
    @classmethod
    def get_sent_requests(cls, user, state: Optional[str] = None, use_cache: bool = True):
        """Get connection requests sent by user."""
        # Try cache first
        if use_cache:
            cached = ConnectionCacheService.get_sent_requests(user.id)
            if cached is not None:
                # Filter by state if needed
                if state:
                    cached = [r for r in cached if r.get('state') == state]
                return cached
        
        # Query database - return QuerySet for pagination support
        queryset = ConnectionRequest.objects.filter(sender=user)
        
        if state:
            queryset = queryset.filter(state=state)
        
        queryset = queryset.select_related('receiver').order_by('-created_at')
        
        return queryset
    
    @classmethod
    def get_received_requests(cls, user, state: Optional[str] = None, use_cache: bool = True):
        """Get connection requests received by user."""
        # Try cache first
        if use_cache:
            cached = ConnectionCacheService.get_received_requests(user.id)
            if cached is not None:
                # Filter by state if needed
                if state:
                    cached = [r for r in cached if r.get('state') == state]
                return cached
        
        # Query database - return QuerySet for pagination support
        queryset = ConnectionRequest.objects.filter(receiver=user)
        
        if state:
            queryset = queryset.filter(state=state)
        
        queryset = queryset.select_related('sender').order_by('-created_at')
        
        return queryset
    
    @classmethod
    def get_accepted_connections(cls, user, use_cache: bool = True):
        """
        Get all accepted connections for user.
        """
        # Try cache first
        if use_cache:
            cached = ConnectionCacheService.get_accepted_connections(user.id)
            if cached is not None:
                return cached
        
        # Query database for accepted connections - return QuerySet for pagination support
        # Return connections where user is either sender or receiver and state is accepted
        queryset = ConnectionRequest.objects.filter(
            Q(sender=user) | Q(receiver=user),
            state=ConnectionRequest.STATE_ACCEPTED
        ).select_related('sender', 'receiver').order_by('-accepted_at')
        
        return queryset
    
    @classmethod
    def get_pending_requests(cls, user) -> Dict[str, List[ConnectionRequest]]:
        """Get all pending requests for user (both sent and received)."""
        sent = cls.get_sent_requests(user, state=ConnectionRequest.STATE_PENDING)
        received = cls.get_received_requests(user, state=ConnectionRequest.STATE_PENDING)
        
        return {
            'sent': sent,
            'received': received
        }
    
    @classmethod
    def are_users_connected(cls, user1, user2) -> bool:
        """Check if two users are connected (accepted)."""
        connection = ConnectionRequest.get_connection(user1, user2)
        return connection is not None
    
    @classmethod
    def get_connection_status(cls, user1, user2) -> Dict[str, Any]:
        """
        Get detailed connection status between two users.
        Returns dict with status, request objects, and metadata.
        """
        # Check both directions
        request_1_to_2 = ConnectionRequest.objects.filter(
            sender=user1,
            receiver=user2
        ).first()
        
        request_2_to_1 = ConnectionRequest.objects.filter(
            sender=user2,
            receiver=user1
        ).first()
        
        status = {
            'connected': False,
            'can_message': False,
            'user1_sent': request_1_to_2 is not None,
            'user2_sent': request_2_to_1 is not None,
            'user1_request_state': request_1_to_2.state if request_1_to_2 else None,
            'user2_request_state': request_2_to_1.state if request_2_to_1 else None,
        }
        
        if request_1_to_2 and request_1_to_2.is_connected():
            status['connected'] = True
            status['can_message'] = request_1_to_2.can_message()
        elif request_2_to_1 and request_2_to_1.is_connected():
            status['connected'] = True
            status['can_message'] = request_2_to_1.can_message()
        
        return status
    
    @classmethod
    def get_connection_statistics(cls, user) -> Dict[str, int]:
        """Get connection statistics for a user."""
        # Try cache first
        cached_count = ConnectionCacheService.get_connection_count(user.id)
        
        if cached_count is None:
            # Calculate from database
            sent_pending = ConnectionRequest.objects.filter(
                sender=user,
                state=ConnectionRequest.STATE_PENDING
            ).count()
            
            received_pending = ConnectionRequest.objects.filter(
                receiver=user,
                state=ConnectionRequest.STATE_PENDING
            ).count()
            
            # Count connections from Connection table (bidirectional)
            connection_count = Connection.objects.filter(
                Q(user1=user) | Q(user2=user)
            ).count()
            
            # Cache the connection count
            ConnectionCacheService.set_connection_count(user.id, connection_count)
        else:
            sent_pending = ConnectionRequest.objects.filter(
                sender=user,
                state=ConnectionRequest.STATE_PENDING
            ).count()
            
            received_pending = ConnectionRequest.objects.filter(
                receiver=user,
                state=ConnectionRequest.STATE_PENDING
            ).count()
            
            connection_count = cached_count
        
        return {
            'sent_pending': sent_pending,
            'received_pending': received_pending,
            'accepted_connections': connection_count,
            'total_requests': sent_pending + received_pending,
        }
