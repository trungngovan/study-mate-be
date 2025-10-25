from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Conversation(models.Model):
    """
    Conversation model for chat between two connected users.
    One-to-one relationship with Connection.
    """
    
    connection = models.OneToOneField(
        'matching.Connection',
        on_delete=models.CASCADE,
        related_name='conversation',
        db_column='connection_id',
        help_text='Link to the connection between two users'
    )
    
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Timestamp of the last message in this conversation'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['-last_message_at'], name='idx_conv_last_msg'),
            models.Index(fields=['created_at'], name='idx_conv_created'),
        ]
        ordering = ['-last_message_at', '-created_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        return f"Conversation: {self.connection}"
    
    def get_participants(self):
        """Return the two users in this conversation."""
        return [self.connection.user1, self.connection.user2]
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        if self.connection.user1 == user:
            return self.connection.user2
        elif self.connection.user2 == user:
            return self.connection.user1
        return None
    
    def is_participant(self, user):
        """Check if a user is a participant in this conversation."""
        return user in self.get_participants()


class Message(models.Model):
    """
    Message model for individual messages in a conversation.
    """
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_column='conversation_id',
        help_text='The conversation this message belongs to'
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_column='sender_id',
        help_text='User who sent the message'
    )
    
    content = models.TextField(
        help_text='Message content'
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Timestamp when the message was read'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['conversation', '-created_at'], name='idx_msg_conv_created'),
            models.Index(fields=['sender', '-created_at'], name='idx_msg_sender_created'),
            models.Index(fields=['conversation', 'read_at'], name='idx_msg_conv_read'),
        ]
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"Message from {self.sender.full_name} at {self.created_at}"
    
    def clean(self):
        """Validate that sender is a participant in the conversation."""
        if self.conversation_id and self.sender_id:
            if not self.conversation.is_participant(self.sender):
                raise ValidationError("Sender must be a participant in the conversation")
    
    def save(self, *args, **kwargs):
        """Override save to run validation and update conversation timestamp."""
        self.clean()
        super().save(*args, **kwargs)
        
        # Update conversation's last_message_at
        from django.utils import timezone
        self.conversation.last_message_at = timezone.now()
        self.conversation.save(update_fields=['last_message_at', 'updated_at'])
    
    def is_read(self):
        """Check if the message has been read."""
        return self.read_at is not None
    
    def mark_as_read(self):
        """Mark the message as read."""
        if not self.is_read():
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])


