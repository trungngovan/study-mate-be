from rest_framework import serializers
from django.utils import timezone
from chat.models import Conversation, Message
from users.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for chat."""
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'avatar_url',
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for message details."""
    
    sender = UserBasicSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'content',
            'read_at',
            'is_read',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'sender',
            'read_at',
            'is_read',
            'created_at',
            'updated_at',
        ]
    
    def get_is_read(self, obj):
        """Return whether the message has been read."""
        return obj.is_read()


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new message."""
    
    class Meta:
        model = Message
        fields = [
            'conversation',
            'content',
        ]
    
    def validate_conversation(self, value):
        """Validate that the user is a participant in the conversation."""
        user = self.context['request'].user
        if not value.is_participant(user):
            raise serializers.ValidationError(
                "You are not a participant in this conversation."
            )
        return value
    
    def validate_content(self, value):
        """Validate that content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """Set sender from request user."""
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class MessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing messages."""
    
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_avatar = serializers.URLField(source='sender.avatar_url', read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id',
            'sender_id',
            'sender_name',
            'sender_avatar',
            'content',
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_is_read(self, obj):
        """Return whether the message has been read."""
        return obj.is_read()


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversation details."""
    
    participants = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'connection',
            'participants',
            'other_participant',
            'last_message',
            'unread_count',
            'last_message_at',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_participants(self, obj):
        """Return both participants in the conversation."""
        participants = obj.get_participants()
        return UserBasicSerializer(participants, many=True).data
    
    def get_other_participant(self, obj):
        """Return the other participant (not the current user)."""
        user = self.context['request'].user
        other = obj.get_other_participant(user)
        if other:
            return UserBasicSerializer(other).data
        return None
    
    def get_last_message(self, obj):
        """Return the last message in the conversation."""
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return MessageListSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        """Return count of unread messages for the current user."""
        user = self.context['request'].user
        return obj.messages.filter(read_at__isnull=True).exclude(sender=user).count()


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing conversations."""
    
    other_participant = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'other_participant',
            'last_message_preview',
            'last_message_at',
            'unread_count',
        ]
        read_only_fields = fields
    
    def get_other_participant(self, obj):
        """Return the other participant (not the current user)."""
        user = self.context['request'].user
        other = obj.get_other_participant(user)
        if other:
            return UserBasicSerializer(other).data
        return None
    
    def get_last_message_preview(self, obj):
        """Return preview of the last message."""
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'content': last_message.content[:100],
                'sender_id': last_message.sender.id,
                'created_at': last_message.created_at,
            }
        return None
    
    def get_unread_count(self, obj):
        """Return count of unread messages for the current user."""
        user = self.context['request'].user
        return obj.messages.filter(read_at__isnull=True).exclude(sender=user).count()


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking message(s) as read."""
    
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of message IDs to mark as read. If not provided, marks all unread messages in conversation."
    )


