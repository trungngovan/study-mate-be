from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class ConnectionRequest(models.Model):
    """
    Model for managing connection requests between users.
    Implements a state machine for connection lifecycle:
    pending -> accepted/rejected/blocked
    """
    
    # State choices
    STATE_PENDING = 'pending'
    STATE_ACCEPTED = 'accepted'
    STATE_REJECTED = 'rejected'
    STATE_BLOCKED = 'blocked'
    
    STATE_CHOICES = [
        (STATE_PENDING, 'Pending'),
        (STATE_ACCEPTED, 'Accepted'),
        (STATE_REJECTED, 'Rejected'),
        (STATE_BLOCKED, 'Blocked'),
    ]
    
    # Valid state transitions
    STATE_TRANSITIONS = {
        STATE_PENDING: [STATE_ACCEPTED, STATE_REJECTED, STATE_BLOCKED],
        STATE_ACCEPTED: [STATE_BLOCKED],
        STATE_REJECTED: [],
        STATE_BLOCKED: [],
    }
    
    # Fields
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_requests',
        db_column='sender_id',
        help_text='User who sent the connection request'
    )
    
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_requests',
        db_column='receiver_id',
        help_text='User who received the connection request'
    )
    
    state = models.CharField(
        max_length=20,
        default=STATE_PENDING,
        choices=STATE_CHOICES,
        db_index=True,
        help_text='Current state of the connection request'
    )
    
    message = models.TextField(
        blank=True,
        default='',
        help_text='Optional message from sender'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'connection_requests'
        unique_together = [['sender', 'receiver']]
        indexes = [
            models.Index(fields=['sender', 'state'], name='idx_conn_req_sender_state'),
            models.Index(fields=['receiver', 'state'], name='idx_conn_req_receiver_state'),
            models.Index(fields=['state', 'created_at'], name='idx_conn_req_state_created'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Connection Request'
        verbose_name_plural = 'Connection Requests'
    
    def __str__(self):
        return f"{self.sender.full_name} -> {self.receiver.full_name} ({self.state})"
    
    def clean(self):
        """Validate that sender and receiver are not the same user."""
        if self.sender_id == self.receiver_id:
            raise ValidationError("Cannot send connection request to yourself")
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    def _transition_state(self, target_state):
        """
        Internal method to handle state transitions.
        Validates that the transition is allowed before changing state.
        """
        if target_state not in self.STATE_TRANSITIONS.get(self.state, []):
            raise ValidationError(
                f"Cannot transition from {self.state} to {target_state}"
            )
        self.state = target_state
    
    # State Transition Methods
    def accept(self):
        """Accept the connection request and create connection immediately."""
        from django.utils import timezone
        self._transition_state(self.STATE_ACCEPTED)
        self.accepted_at = timezone.now()
        self.save()
    
    def reject(self):
        """Reject the connection request."""
        from django.utils import timezone
        self._transition_state(self.STATE_REJECTED)
        self.rejected_at = timezone.now()
        self.save()
    
    def block(self):
        """Block the connection."""
        self._transition_state(self.STATE_BLOCKED)
        self.save()
    
    @classmethod
    def get_connection(cls, user1, user2):
        """
        Get any accepted connection between two users.
        Returns the connection request object if accepted, None otherwise.
        """
        try:
            # Check if there's an accepted connection in either direction
            request = cls.objects.filter(
                models.Q(sender=user1, receiver=user2) | models.Q(sender=user2, receiver=user1),
                state=cls.STATE_ACCEPTED
            ).first()
            return request
        except cls.DoesNotExist:
            return None
    
    def is_connected(self):
        """Check if this connection is accepted (users are connected)."""
        return self.state == self.STATE_ACCEPTED
    
    def can_message(self):
        """Check if users can message each other (connection is accepted)."""
        return self.state == self.STATE_ACCEPTED


class Connection(models.Model):
    """
    Simplified view of accepted connections for easy querying.
    This is a denormalized model for performance optimization.
    """
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connections_as_user1',
        db_column='user1_id'
    )
    
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='connections_as_user2',
        db_column='user2_id'
    )
    
    connection_request = models.ForeignKey(
        ConnectionRequest,
        on_delete=models.CASCADE,
        related_name='connection_records',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'connections'
        unique_together = [['user1', 'user2']]
        indexes = [
            models.Index(fields=['user1', 'created_at'], name='idx_conn_user1_created'),
            models.Index(fields=['user2', 'created_at'], name='idx_conn_user2_created'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Connection'
        verbose_name_plural = 'Connections'
    
    def __str__(self):
        return f"{self.user1.full_name} <-> {self.user2.full_name}"
    
    def clean(self):
        """Ensure user1_id < user2_id for consistency."""
        if hasattr(self, 'user1') and hasattr(self, 'user2'):
            if self.user1.id > self.user2.id:
                self.user1, self.user2 = self.user2, self.user1
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def create_from_request(cls, connection_request):
        """Create a Connection record from an accepted ConnectionRequest."""
        user1, user2 = connection_request.sender, connection_request.receiver
        
        # Ensure user1_id < user2_id for consistency
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        connection, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2,
            defaults={'connection_request': connection_request}
        )
        
        return connection, created
