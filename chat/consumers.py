import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from chat.models import Conversation, Message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.
    
    Handles:
    - Connecting to a conversation room
    - Sending messages
    - Receiving messages
    - Typing indicators
    - Message read receipts
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Extract conversation ID from URL and join the room.
        """
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        logger.info(f"WebSocket connection attempt - Conversation: {self.conversation_id}, User: {self.user}")
        
        # Check if user is authenticated
        if self.user.is_anonymous:
            logger.warning(f"WebSocket rejected: User not authenticated (conversation_id={self.conversation_id})")
            await self.close(code=4001)
            return
        
        # Check if user is a participant in the conversation
        is_participant = await self.check_participant()
        if not is_participant:
            logger.warning(f"WebSocket rejected: User {self.user.id} not participant in conversation {self.conversation_id}")
            await self.close(code=4003)
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"WebSocket accepted: User {self.user.id} connected to conversation {self.conversation_id}")
        
        # Send connection success message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat'
        }))
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Leave the room group.
        """
        user_info = f"User {self.user.id}" if hasattr(self, 'user') and not self.user.is_anonymous else "Anonymous"
        conv_id = self.conversation_id if hasattr(self, 'conversation_id') else "Unknown"
        logger.info(f"WebSocket disconnected: {user_info} from conversation {conv_id} (code={close_code})")
        
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle messages received from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.debug(f"WebSocket received from User {self.user.id}: type={message_type}")
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(data)
            elif message_type == 'message_read':
                await self.handle_message_read(data)
            else:
                logger.warning(f"Unknown message type from User {self.user.id}: {message_type}")
                await self.send_error('Unknown message type')
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from User {self.user.id}: {text_data}")
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"Error handling message from User {self.user.id}: {str(e)}", exc_info=True)
            await self.send_error(f'Error: {str(e)}')
    
    async def handle_chat_message(self, data):
        """
        Handle incoming chat message.
        Save to database and broadcast to room.
        """
        content = data.get('content', '').strip()
        
        if not content:
            await self.send_error('Message content cannot be empty')
            return
        
        # Save message to database
        message = await self.save_message(content)
        
        if message:
            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender_id': self.user.id,
                    'sender_name': self.user.full_name,
                    'sender_avatar': self.user.avatar_url,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                }
            )
    
    async def handle_typing_indicator(self, data):
        """
        Handle typing indicator.
        Broadcast to other participants.
        """
        is_typing = data.get('is_typing', False)
        
        # Broadcast to room group (except sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'user_name': self.user.full_name,
                'is_typing': is_typing,
            }
        )
    
    async def handle_message_read(self, data):
        """
        Handle message read receipt.
        Update database and broadcast to sender.
        """
        message_ids = data.get('message_ids', [])
        
        if message_ids:
            marked_count = await self.mark_messages_read(message_ids)
            
            # Broadcast to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'message_ids': message_ids,
                    'read_at': timezone.now().isoformat(),
                }
            )
    
    # WebSocket message handlers (called by group_send)
    
    async def chat_message(self, event):
        """
        Send chat message to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event['sender_avatar'],
            'content': event['content'],
            'created_at': event['created_at'],
        }))
    
    async def typing_indicator(self, event):
        """
        Send typing indicator to WebSocket.
        Don't send to the user who is typing.
        """
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing'],
            }))
    
    async def messages_read(self, event):
        """
        Send message read receipt to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id'],
            'message_ids': event['message_ids'],
            'read_at': event['read_at'],
        }))
    
    # Helper methods
    
    async def send_error(self, error_message):
        """
        Send error message to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
        }))
    
    @database_sync_to_async
    def check_participant(self):
        """
        Check if user is a participant in the conversation.
        """
        try:
            conversation = Conversation.objects.select_related(
                'connection__connection_request'
            ).get(id=self.conversation_id)
            
            # Check if user is participant
            if not conversation.is_participant(self.user):
                return False
            
            # Check if connection is accepted
            connection_request = conversation.connection.connection_request
            if connection_request and not connection_request.can_message():
                return False
            
            return True
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database.
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content
            )
            
            logger.info(f"Message saved: ID={message.id}, User={self.user.id}, Conversation={self.conversation_id}")
            return message
        except Exception as e:
            logger.error(f"Error saving message for User {self.user.id} in conversation {self.conversation_id}: {e}", exc_info=True)
            return None
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """
        Mark messages as read in database.
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            # Get unread messages (not sent by current user)
            unread_messages = conversation.messages.filter(
                id__in=message_ids,
                read_at__isnull=True
            ).exclude(sender=self.user)
            
            # Mark as read
            marked_count = unread_messages.update(read_at=timezone.now())
            
            return marked_count
        except Exception as e:
            print(f"Error marking messages as read: {e}")
            return 0

