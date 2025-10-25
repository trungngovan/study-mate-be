from chat.models import Conversation, Message
from matching.models import Connection


class ConversationService:
    """
    Service for managing conversations.
    """
    
    @classmethod
    def get_or_create_conversation(cls, connection):
        """
        Get or create a conversation for a connection.
        Automatically creates conversation when a connection is accepted.
        
        Args:
            connection: Connection instance
            
        Returns:
            Conversation instance
        """
        conversation, created = Conversation.objects.get_or_create(
            connection=connection
        )
        return conversation
    
    @classmethod
    def get_conversation_for_users(cls, user1, user2):
        """
        Get conversation between two users if they have an accepted connection.
        
        Args:
            user1: First user
            user2: Second user
            
        Returns:
            Conversation instance or None
        """
        try:
            # Find connection between users (either direction)
            from django.db.models import Q
            connection = Connection.objects.filter(
                Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
            ).first()
            
            if connection and connection.connection_request:
                # Check if connection is accepted
                if connection.connection_request.can_message():
                    return cls.get_or_create_conversation(connection)
            
            return None
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return None
    
    @classmethod
    def get_unread_count(cls, conversation, user):
        """
        Get count of unread messages for a user in a conversation.
        
        Args:
            conversation: Conversation instance
            user: User instance
            
        Returns:
            int: Count of unread messages
        """
        return conversation.messages.filter(
            read_at__isnull=True
        ).exclude(sender=user).count()
    
    @classmethod
    def mark_all_messages_read(cls, conversation, user):
        """
        Mark all unread messages as read for a user in a conversation.
        
        Args:
            conversation: Conversation instance
            user: User instance
            
        Returns:
            int: Number of messages marked as read
        """
        from django.utils import timezone
        
        unread_messages = conversation.messages.filter(
            read_at__isnull=True
        ).exclude(sender=user)
        
        marked_count = unread_messages.update(read_at=timezone.now())
        return marked_count


