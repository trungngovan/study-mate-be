# Chat Feature

Real-time chat functionality for accepted connections using Django Channels and WebSocket.

## Overview

The chat feature allows users who have accepted connections to message each other in real-time. It consists of:

1. **REST API** (HTTP) for retrieving conversations and message history
2. **WebSocket API** for real-time messaging, typing indicators, and read receipts

## Architecture

### Models

- **Conversation**: One-to-one with Connection. Automatically created when connection is accepted.
- **Message**: Chat messages with sender, content, read status, and timestamps.

### REST API Endpoints

#### Conversations

- `GET /api/chat/conversations/` - List all conversations
- `GET /api/chat/conversations/{id}/` - Get conversation details
- `GET /api/chat/conversations/{id}/messages/` - Get message history (paginated)
- `POST /api/chat/conversations/{id}/mark_read/` - Mark messages as read

#### Messages

- `POST /api/chat/messages/` - Send a message (HTTP fallback)
- `GET /api/chat/messages/{id}/` - Get message details

### WebSocket API

**Connection URL**: `ws://localhost:8000/ws/chat/{conversation_id}/?token={jwt_token}`

Or with Bearer token in Authorization header.

#### Events to Send (Client → Server)

1. **Send Message**
```json
{
  "type": "chat_message",
  "content": "Hello!"
}
```

2. **Typing Indicator**
```json
{
  "type": "typing_indicator",
  "is_typing": true
}
```

3. **Mark Messages as Read**
```json
{
  "type": "message_read",
  "message_ids": [1, 2, 3]
}
```

#### Events to Receive (Server → Client)

1. **Connection Established**
```json
{
  "type": "connection_established",
  "message": "Connected to chat"
}
```

2. **New Message**
```json
{
  "type": "chat_message",
  "message_id": 123,
  "sender_id": 456,
  "sender_name": "John Doe",
  "sender_avatar": "https://...",
  "content": "Hello!",
  "created_at": "2025-10-25T10:00:00Z"
}
```

3. **Typing Indicator**
```json
{
  "type": "typing_indicator",
  "user_id": 456,
  "user_name": "John Doe",
  "is_typing": true
}
```

4. **Messages Read**
```json
{
  "type": "messages_read",
  "user_id": 456,
  "message_ids": [1, 2, 3],
  "read_at": "2025-10-25T10:00:00Z"
}
```

5. **Error**
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Authentication

### REST API
Use standard JWT Bearer token in Authorization header:
```
Authorization: Bearer <access_token>
```

### WebSocket
Pass JWT token in query string or Authorization header:
- Query string: `ws://localhost:8000/ws/chat/1/?token=<access_token>`
- Header: `Authorization: Bearer <access_token>`

## Permissions

- Users must be participants in a conversation to access it
- Users can only message in accepted connections
- Messages cannot be edited or deleted

## Usage Example

### JavaScript WebSocket Client

```javascript
// Connect to chat
const token = 'your_jwt_access_token';
const conversationId = 1;
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${conversationId}/?token=${token}`);

// Connection opened
ws.onopen = () => {
  console.log('Connected to chat');
};

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'chat_message':
      console.log('New message:', data.content);
      break;
    case 'typing_indicator':
      console.log(`${data.user_name} is typing...`);
      break;
    case 'messages_read':
      console.log('Messages marked as read');
      break;
  }
};

// Send message
ws.send(JSON.stringify({
  type: 'chat_message',
  content: 'Hello!'
}));

// Send typing indicator
ws.send(JSON.stringify({
  type: 'typing_indicator',
  is_typing: true
}));

// Mark messages as read
ws.send(JSON.stringify({
  type: 'message_read',
  message_ids: [1, 2, 3]
}));
```

## Database Migrations

Run migrations to create chat tables:
```bash
python manage.py migrate chat
```

## Redis Configuration

Chat requires Redis for:
1. Channel layers (WebSocket message routing)
2. Caching (optional)

Redis URL is configured via environment variable:
```
REDIS_URL=redis://127.0.0.1:6379/0
```

## Running the Server

Use Daphne (ASGI server) instead of Django's development server:

```bash
# Development
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# Or with Django's runserver (includes ASGI support)
python manage.py runserver
```

## Features

- ✅ Real-time messaging
- ✅ Message read receipts
- ✅ Typing indicators
- ✅ Message history pagination
- ✅ Unread message count
- ✅ JWT authentication for WebSocket
- ✅ Permission validation
- ✅ Auto-create conversation on connection accept
- ✅ Optimized database queries

## Future Enhancements (Not Implemented)

- Message delivery status (sent, delivered, read)
- Online/offline status
- Message attachments
- Message reactions
- Message search
- Push notifications


