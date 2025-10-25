from rest_framework import permissions
from chat.models import Conversation, Message


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to only allow participants of a conversation to access it.
    """
    
    message = "You are not a participant in this conversation."
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return obj.is_participant(request.user)
        elif isinstance(obj, Message):
            return obj.conversation.is_participant(request.user)
        return False


class CanMessageConnection(permissions.BasePermission):
    """
    Permission to only allow messaging in accepted connections.
    """
    
    message = "You can only message users you are connected with (accepted connections)."
    
    def has_permission(self, request, view):
        # For conversation list, always allow (will be filtered in queryset)
        if view.action in ['list', 'retrieve']:
            return True
        
        # For creating messages, check if conversation exists and is valid
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                try:
                    conversation = Conversation.objects.select_related(
                        'connection__connection_request'
                    ).get(id=conversation_id)
                    
                    # Check if user is participant
                    if not conversation.is_participant(request.user):
                        return False
                    
                    # Check if connection is accepted
                    connection_request = conversation.connection.connection_request
                    if connection_request and connection_request.can_message():
                        return True
                    
                    return False
                except Conversation.DoesNotExist:
                    return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            connection_request = obj.connection.connection_request
            if connection_request:
                return connection_request.can_message() and obj.is_participant(request.user)
        elif isinstance(obj, Message):
            connection_request = obj.conversation.connection.connection_request
            if connection_request:
                return connection_request.can_message() and obj.conversation.is_participant(request.user)
        
        return False


