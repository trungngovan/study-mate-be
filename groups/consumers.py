"""
WebSocket consumers for groups app.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from groups.models import StudyGroup, GroupConversation, GroupMessage, GroupMessageRead

logger = logging.getLogger(__name__)


class GroupChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time group chat functionality.

    Handles:
    - Connecting to a group conversation room
    - Sending messages
    - Receiving messages
    - Typing indicators
    - Message read receipts
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        Extract group ID from URL and join the room.
        """
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'group_chat_{self.group_id}'
        self.user = self.scope['user']

        logger.info(f"WebSocket connection attempt - Group: {self.group_id}, User: {self.user}")

        # Check if user is authenticated
        if self.user.is_anonymous:
            logger.warning(f"WebSocket rejected: User not authenticated (group_id={self.group_id})")
            await self.close(code=4001)
            return

        # Check if user is a member of the group
        is_member = await self.check_member()
        if not is_member:
            logger.warning(f"WebSocket rejected: User {self.user.id} not member of group {self.group_id}")
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(f"WebSocket accepted: User {self.user.id} connected to group {self.group_id}")

        # Send connection success message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to group chat'
        }))

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Leave the room group.
        """
        user_info = f"User {self.user.id}" if hasattr(self, 'user') and not self.user.is_anonymous else "Anonymous"
        group_id = self.group_id if hasattr(self, 'group_id') else "Unknown"
        logger.info(f"WebSocket disconnected: {user_info} from group {group_id} (code={close_code})")

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
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error processing message from User {self.user.id}: {str(e)}", exc_info=True)
            await self.send_error(f'Server error: {str(e)}')

    async def handle_chat_message(self, data):
        """
        Handle incoming chat message.
        Save to database and broadcast to group.
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
                    'sender_name': self.user.full_name or self.user.email,
                    'sender_avatar': self.user.avatar_url,
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                }
            )

            logger.info(f"Message {message.id} sent by User {self.user.id} in group {self.group_id}")

    async def handle_typing_indicator(self, data):
        """
        Handle typing indicator.
        Broadcast to other users in the group.
        """
        is_typing = data.get('is_typing', False)

        # Broadcast typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'user_name': self.user.full_name or self.user.email,
                'is_typing': is_typing,
            }
        )

    async def handle_message_read(self, data):
        """
        Handle message read receipts.
        Mark messages as read and broadcast to group.
        """
        message_ids = data.get('message_ids', [])

        if not message_ids:
            await self.send_error('No message IDs provided')
            return

        # Mark messages as read
        read_count = await self.mark_messages_read(message_ids)

        if read_count > 0:
            # Broadcast read receipts to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'message_ids': message_ids,
                    'read_at': timezone.now().isoformat(),
                }
            )

            logger.info(f"User {self.user.id} marked {read_count} messages as read in group {self.group_id}")

    # Event handlers for channel layer messages
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
        Send message read receipts to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id'],
            'message_ids': event['message_ids'],
            'read_at': event['read_at'],
        }))

    async def send_error(self, message):
        """
        Send error message to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    # Database operations (sync functions wrapped with database_sync_to_async)
    @database_sync_to_async
    def check_member(self):
        """
        Check if user is a member of the group.
        """
        try:
            group = StudyGroup.objects.get(pk=self.group_id)
            return group.is_member(self.user)
        except StudyGroup.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database.
        """
        try:
            group = StudyGroup.objects.get(pk=self.group_id)

            # Get or create conversation
            conversation, created = GroupConversation.objects.get_or_create(group=group)

            # Create message
            message = GroupMessage.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content
            )

            return message
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}", exc_info=True)
            return None

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """
        Mark messages as read for the current user.
        Returns number of messages marked as read.
        """
        try:
            # Filter message IDs to only those in this group's conversation
            group = StudyGroup.objects.get(pk=self.group_id)
            conversation = group.conversation

            valid_messages = GroupMessage.objects.filter(
                id__in=message_ids,
                conversation=conversation
            ).exclude(
                sender=self.user  # Don't mark own messages as read
            )

            # Bulk create read records (ignore conflicts if already read)
            read_records = []
            for message in valid_messages:
                if not GroupMessageRead.objects.filter(message=message, user=self.user).exists():
                    read_records.append(
                        GroupMessageRead(message=message, user=self.user)
                    )

            GroupMessageRead.objects.bulk_create(read_records, ignore_conflicts=True)

            return len(read_records)
        except Exception as e:
            logger.error(f"Error marking messages as read: {str(e)}", exc_info=True)
            return 0
