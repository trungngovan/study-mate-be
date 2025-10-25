"""
Serializers for matching app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import ConnectionRequest, Connection


User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for connection requests."""
    
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
            'bio',
        ]
        read_only_fields = fields


class ConnectionRequestSerializer(serializers.ModelSerializer):
    """Serializer for connection request details."""
    
    sender = UserBasicSerializer(read_only=True)
    receiver = UserBasicSerializer(read_only=True)
    can_accept = serializers.SerializerMethodField()
    can_reject = serializers.SerializerMethodField()
    can_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ConnectionRequest
        fields = [
            'id',
            'sender',
            'receiver',
            'state',
            'message',
            'created_at',
            'updated_at',
            'accepted_at',
            'rejected_at',
            'can_accept',
            'can_reject',
            'can_message',
        ]
        read_only_fields = [
            'id',
            'sender',
            'receiver',
            'state',
            'created_at',
            'updated_at',
            'accepted_at',
            'rejected_at',
        ]
    
    def get_can_accept(self, obj):
        """Check if the current user can accept this request."""
        request = self.context.get('request')
        if request and request.user:
            return (
                obj.receiver == request.user and
                obj.state == ConnectionRequest.STATE_PENDING
            )
        return False
    
    def get_can_reject(self, obj):
        """Check if the current user can reject this request."""
        request = self.context.get('request')
        if request and request.user:
            return (
                obj.receiver == request.user and
                obj.state == ConnectionRequest.STATE_PENDING
            )
        return False
    
    def get_can_message(self, obj):
        """Check if users can message each other."""
        return obj.can_message()


class SendConnectionRequestSerializer(serializers.Serializer):
    """Serializer for sending a connection request."""
    
    receiver_id = serializers.IntegerField(required=True)
    message = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default=''
    )
    
    def validate_receiver_id(self, value):
        """Validate that receiver exists and is not the sender."""
        try:
            receiver = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver user does not exist")
        
        # Check if sender is trying to send to themselves
        request = self.context.get('request')
        if request and request.user.id == value:
            raise serializers.ValidationError("Cannot send connection request to yourself")
        
        return value
    
    def validate(self, data):
        """Additional validation."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")
        
        # Check if request already exists
        receiver_id = data.get('receiver_id')
        existing = ConnectionRequest.objects.filter(
            sender=request.user,
            receiver_id=receiver_id,
            state__in=[
                ConnectionRequest.STATE_PENDING,
                ConnectionRequest.STATE_ACCEPTED,
            ]
        ).first()
        
        if existing:
            raise serializers.ValidationError(
                f"Connection request already exists with status: {existing.state}"
            )
        
        return data


class AcceptConnectionRequestSerializer(serializers.Serializer):
    """Serializer for accepting a connection request."""
    pass


class RejectConnectionRequestSerializer(serializers.Serializer):
    """Serializer for rejecting a connection request."""
    pass


class ConnectionSerializer(serializers.ModelSerializer):
    """Serializer for accepted connections."""
    
    user1 = UserBasicSerializer(read_only=True)
    user2 = UserBasicSerializer(read_only=True)
    connection_state = serializers.SerializerMethodField()
    
    class Meta:
        model = Connection
        fields = [
            'id',
            'user1',
            'user2',
            'created_at',
            'connection_state',
        ]
        read_only_fields = fields
    
    def get_connection_state(self, obj):
        """Get the state of the underlying connection request."""
        if obj.connection_request:
            return obj.connection_request.state
        return None


class ConnectionRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing connection requests."""
    
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_avatar = serializers.URLField(source='sender.avatar_url', read_only=True)
    receiver_name = serializers.CharField(source='receiver.full_name', read_only=True)
    receiver_avatar = serializers.URLField(source='receiver.avatar_url', read_only=True)
    
    class Meta:
        model = ConnectionRequest
        fields = [
            'id',
            'sender_name',
            'sender_avatar',
            'receiver_name',
            'receiver_avatar',
            'state',
            'message',
            'created_at',
        ]
        read_only_fields = fields


class ConnectionStatusSerializer(serializers.Serializer):
    """Serializer for connection status between two users."""
    
    connected = serializers.BooleanField()
    can_message = serializers.BooleanField()
    user1_sent = serializers.BooleanField()
    user2_sent = serializers.BooleanField()
    user1_request_state = serializers.CharField(allow_null=True)
    user2_request_state = serializers.CharField(allow_null=True)


class ConnectionStatisticsSerializer(serializers.Serializer):
    """Serializer for user connection statistics."""
    
    sent_pending = serializers.IntegerField()
    received_pending = serializers.IntegerField()
    accepted_connections = serializers.IntegerField()
    total_requests = serializers.IntegerField()


class AcceptedConnectionSerializer(serializers.Serializer):
    """Serializer for accepted connection with user details."""
    
    id = serializers.IntegerField()
    user = UserBasicSerializer()
    connection_state = serializers.CharField()
    accepted_at = serializers.DateTimeField()
    can_message = serializers.BooleanField()
    conversation_id = serializers.IntegerField(allow_null=True)
    
    def to_representation(self, instance):
        """
        Custom representation to show the other user in the connection.
        """
        request = self.context.get('request')
        if not request or not request.user:
            return super().to_representation(instance)
        
        current_user = request.user
        
        # Determine which user to show (the other user in the connection)
        if instance.sender == current_user:
            other_user = instance.receiver
        else:
            other_user = instance.sender
        
        user_serializer = UserBasicSerializer(other_user)
        
        # Get conversation_id if exists
        conversation_id = None
        try:
            # Try to get connection and its conversation
            from matching.models import Connection
            connection = Connection.objects.filter(
                connection_request=instance
            ).select_related('conversation').first()
            
            if connection and hasattr(connection, 'conversation'):
                conversation_id = connection.conversation.id
        except Exception:
            pass
        
        return {
            'id': instance.id,
            'user': user_serializer.data,
            'connection_state': instance.state,
            'accepted_at': instance.accepted_at,
            'can_message': instance.can_message(),
            'conversation_id': conversation_id,
        }
