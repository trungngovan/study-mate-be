# Study Mate API Documentation

## Base URL
`http://localhost:8000`

## Interactive Docs
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`

## Authentication

All endpoints require JWT authentication except `/auth/register/` and `/auth/login/`.

**Login to get token:**
```bash
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}
```

**Use token in headers:**
```
Authorization: Bearer <access_token>
```

---

## 🔐 Authentication `/api/auth/`

### POST `/api/auth/register/`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "school": 1,
  "major": "Computer Science",
  "year": 2,
  "bio": "Hello!",
  "avatar_url": "https://example.com/avatar.jpg",
  "learning_radius_km": 5.0,
  "privacy_level": "open"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "phone": "+1234567890",
    "full_name": "John Doe",
    "school": 1,
    "school_name": "University Name",
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!",
    "avatar_url": "https://example.com/avatar.jpg",
    "learning_radius_km": 5.0,
    "privacy_level": "open",
    "status": "active",
    "last_active_at": null,
    "created_at": "2025-10-24T10:00:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### POST `/api/auth/login/`
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "phone": "+1234567890",
    "full_name": "John Doe",
    "school": 1,
    "school_name": "University Name",
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!",
    "avatar_url": "https://example.com/avatar.jpg",
    "learning_radius_km": 5.0,
    "privacy_level": "open",
    "status": "active",
    "last_active_at": "2025-10-24T10:00:00Z",
    "created_at": "2025-10-20T10:00:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### POST `/api/auth/logout/`
Logout user by blacklisting refresh token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

### POST `/api/auth/token/refresh/`
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### GET `/api/auth/profile/`
Get current user's profile.

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone": "+1234567890",
  "full_name": "John Doe",
  "school": 1,
  "school_name": "University Name",
  "major": "Computer Science",
  "year": 2,
  "bio": "Hello!",
  "avatar_url": "https://example.com/avatar.jpg",
  "learning_radius_km": 5.0,
  "privacy_level": "open",
  "status": "active",
  "last_active_at": "2025-10-24T10:00:00Z",
  "created_at": "2025-10-20T10:00:00Z"
}
```

### PUT/PATCH `/api/auth/profile/`
Update current user's profile.

**Request:**
```json
{
  "full_name": "John Smith",
  "bio": "Updated bio",
  "major": "Software Engineering",
  "year": 3
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone": "+1234567890",
  "full_name": "John Smith",
  "school": 1,
  "school_name": "University Name",
  "major": "Software Engineering",
  "year": 3,
  "bio": "Updated bio",
  "avatar_url": "https://example.com/avatar.jpg",
  "learning_radius_km": 5.0,
  "privacy_level": "open",
  "status": "active",
  "last_active_at": "2025-10-24T10:00:00Z",
  "created_at": "2025-10-20T10:00:00Z"
}
```

### POST `/api/auth/change-password/`
Change user's password.

**Request:**
```json
{
  "old_password": "password123",
  "new_password": "newpassword456",
  "new_password_confirm": "newpassword456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

---

## 📍 Location `/api/users/location/`

### POST `/api/users/location/`
Update user's current location.

**Request:**
```json
{
  "latitude": 21.028511,
  "longitude": 105.804817,
  "accuracy": 15.5
}
```

**Response (200):**
```json
{
  "updated": true,
  "saved_to_history": true,
  "distance_moved": 150.5,
  "time_since_last": 1200,
  "message": "Location saved: moved 150.5m and 20.0 minutes passed",
  "latitude": 21.028511,
  "longitude": 105.804817,
  "timestamp": "2025-10-24T10:00:00Z"
}
```

### GET `/api/users/location/current/`
Get user's current location.

**Response (200):**
```json
{
  "latitude": 21.028511,
  "longitude": 105.804817,
  "last_updated": "2025-10-24T10:00:00Z"
}
```

### GET `/api/users/location/history/`
Get user's location history with pagination.

**Query Parameters:**
- `limit` (default: 50)
- `from_date` (ISO datetime)
- `to_date` (ISO datetime)

**Response (200):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/users/location/history/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "latitude": 21.028511,
      "longitude": 105.804817,
      "recorded_at": "2025-10-24T10:00:00Z",
      "accuracy": 15.5
    }
  ]
}
```

### GET `/api/users/location/history/{id}/`
Get specific location history entry.

**Response (200):**
```json
{
  "id": 1,
  "user": 1,
  "user_email": "user@example.com",
  "user_name": "John Doe",
  "latitude": 21.028511,
  "longitude": 105.804817,
  "recorded_at": "2025-10-24T10:00:00Z",
  "accuracy": 15.5,
  "created_at": "2025-10-24T10:00:00Z"
}
```

### GET `/api/users/location/stats/`
Get location statistics.

**Query Parameters:**
- `days` (default: 30)

**Response (200):**
```json
{
  "total_records": 45,
  "days_analyzed": 30,
  "first_recorded": "2025-09-24T10:00:00Z",
  "last_recorded": "2025-10-24T10:00:00Z",
  "current_location": {
    "latitude": 21.028511,
    "longitude": 105.804817
  }
}
```

---

## 🔍 Discover `/api/discover/`

### GET `/api/discover/nearby-learners/`
Find nearby learners within specified radius.

**Query Parameters:**
- `radius` (default: user's learning_radius_km)

**Response (200):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/discover/nearby-learners/?page=2",
  "previous": null,
  "radius_km": 5.0,
  "results": [
    {
      "id": 2,
      "email": "user2@example.com",
      "full_name": "Jane Smith",
      "avatar_url": "https://example.com/avatar2.jpg",
      "bio": "Hello!",
      "school_name": "University Name",
      "major": "Computer Science",
      "year": 2,
      "distance_km": 0.15,
      "latitude": 21.028611,
      "longitude": 105.804917
    }
  ]
}
```

---

## 🤝 Matching

### Connection Requests `/api/matching/requests/`

#### POST `/api/matching/requests/`
Send a connection request to another user.

**Request:**
```json
{
  "receiver_id": 123,
  "message": "Hi! Want to study together?"
}
```

**Response (201):**
```json
{
  "id": 1,
  "sender": {
    "id": 456,
    "email": "sender@example.com",
    "full_name": "Alice",
    "avatar_url": "https://example.com/avatar.jpg",
    "school": 1,
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!"
  },
  "receiver": {
    "id": 123,
    "email": "receiver@example.com",
    "full_name": "Bob",
    "avatar_url": "https://example.com/avatar2.jpg",
    "school": 1,
    "major": "Engineering",
    "year": 3,
    "bio": "Hi there!"
  },
  "state": "pending",
  "message": "Hi! Want to study together?",
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z",
  "accepted_at": null,
  "rejected_at": null,
  "can_accept": false,
  "can_reject": false,
  "can_message": false
}
```

#### GET `/api/matching/requests/`
List all connection requests (sent and received) with pagination.

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

**Response (200):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/matching/requests/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "sender_name": "Alice",
      "sender_avatar": "https://example.com/avatar.jpg",
      "receiver_name": "Bob",
      "receiver_avatar": "https://example.com/avatar2.jpg",
      "state": "pending",
      "message": "Hi! Want to study together?",
      "created_at": "2025-10-24T10:00:00Z"
    }
  ]
}
```

#### GET `/api/matching/requests/{id}/`
Get details of a specific connection request.

**Response (200):**
```json
{
  "id": 1,
  "sender": {
    "id": 456,
    "email": "sender@example.com",
    "full_name": "Alice",
    "avatar_url": "https://example.com/avatar.jpg",
    "school": 1,
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!"
  },
  "receiver": {
    "id": 123,
    "email": "receiver@example.com",
    "full_name": "Bob",
    "avatar_url": "https://example.com/avatar2.jpg",
    "school": 1,
    "major": "Engineering",
    "year": 3,
    "bio": "Hi there!"
  },
  "state": "pending",
  "message": "Hi! Want to study together?",
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z",
  "accepted_at": null,
  "rejected_at": null,
  "can_accept": true,
  "can_reject": true,
  "can_message": false
}
```

#### GET `/api/matching/requests/sent/`
List connection requests sent by current user with pagination.

**Query Parameters:**
- `state` (optional: pending, accepted, rejected, blocked)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

**Response (200):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/matching/requests/sent/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "sender_name": "Alice",
      "sender_avatar": "https://example.com/avatar.jpg",
      "receiver_name": "Bob",
      "receiver_avatar": "https://example.com/avatar2.jpg",
      "state": "pending",
      "message": "Hi! Want to study together?",
      "created_at": "2025-10-24T10:00:00Z"
    }
  ]
}
```

#### GET `/api/matching/requests/received/`
List connection requests received by current user with pagination.

**Query Parameters:**
- `state` (optional: pending, accepted, rejected, blocked)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

**Response (200):**
```json
{
  "count": 12,
  "next": "http://localhost:8000/api/matching/requests/received/?page=2",
  "previous": null,
  "results": [
    {
      "id": 2,
      "sender_name": "Charlie",
      "sender_avatar": "https://example.com/avatar3.jpg",
      "receiver_name": "Alice",
      "receiver_avatar": "https://example.com/avatar.jpg",
      "state": "pending",
      "message": "Let's study together!",
      "created_at": "2025-10-24T09:00:00Z"
    }
  ]
}
```

#### GET `/api/matching/requests/pending/`
List all pending requests (both sent and received).

**Response (200):**
```json
{
  "sent": [
    {
      "id": 1,
      "sender_name": "Alice",
      "sender_avatar": "https://example.com/avatar.jpg",
      "receiver_name": "Bob",
      "receiver_avatar": "https://example.com/avatar2.jpg",
      "state": "pending",
      "message": "Hi! Want to study together?",
      "created_at": "2025-10-24T10:00:00Z"
    }
  ],
  "received": [
    {
      "id": 2,
      "sender_name": "Charlie",
      "sender_avatar": "https://example.com/avatar3.jpg",
      "receiver_name": "Alice",
      "receiver_avatar": "https://example.com/avatar.jpg",
      "state": "pending",
      "message": "Let's study together!",
      "created_at": "2025-10-24T09:00:00Z"
    }
  ]
}
```

#### DELETE `/api/matching/requests/{id}/`
Cancel a sent connection request (only pending requests).

**Response (204):** No content

#### POST `/api/matching/requests/{id}/accept/`
Accept a connection request.

**Response (200):**
```json
{
  "id": 1,
  "sender": {
    "id": 456,
    "email": "sender@example.com",
    "full_name": "Alice",
    "avatar_url": "https://example.com/avatar.jpg",
    "school": 1,
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!"
  },
  "receiver": {
    "id": 123,
    "email": "receiver@example.com",
    "full_name": "Bob",
    "avatar_url": "https://example.com/avatar2.jpg",
    "school": 1,
    "major": "Engineering",
    "year": 3,
    "bio": "Hi there!"
  },
  "state": "accepted",
  "message": "Hi! Want to study together?",
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:05:00Z",
  "accepted_at": "2025-10-24T10:05:00Z",
  "rejected_at": null,
  "can_accept": false,
  "can_reject": false,
  "can_message": true
}
```

#### POST `/api/matching/requests/{id}/reject/`
Reject a connection request.

**Response (200):**
```json
{
  "id": 1,
  "sender": {
    "id": 456,
    "email": "sender@example.com",
    "full_name": "Alice",
    "avatar_url": "https://example.com/avatar.jpg",
    "school": 1,
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!"
  },
  "receiver": {
    "id": 123,
    "email": "receiver@example.com",
    "full_name": "Bob",
    "avatar_url": "https://example.com/avatar2.jpg",
    "school": 1,
    "major": "Engineering",
    "year": 3,
    "bio": "Hi there!"
  },
  "state": "rejected",
  "message": "Hi! Want to study together?",
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:05:00Z",
  "accepted_at": null,
  "rejected_at": "2025-10-24T10:05:00Z",
  "can_accept": false,
  "can_reject": false,
  "can_message": false
}
```

#### POST `/api/matching/requests/{id}/block/`
Block a connection.

**Response (200):**
```json
{
  "id": 1,
  "sender": {
    "id": 456,
    "email": "sender@example.com",
    "full_name": "Alice",
    "avatar_url": "https://example.com/avatar.jpg",
    "school": 1,
    "major": "Computer Science",
    "year": 2,
    "bio": "Hello!"
  },
  "receiver": {
    "id": 123,
    "email": "receiver@example.com",
    "full_name": "Bob",
    "avatar_url": "https://example.com/avatar2.jpg",
    "school": 1,
    "major": "Engineering",
    "year": 3,
    "bio": "Hi there!"
  },
  "state": "blocked",
  "message": "Hi! Want to study together?",
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:05:00Z",
  "accepted_at": null,
  "rejected_at": null,
  "can_accept": false,
  "can_reject": false,
  "can_message": false
}
```

### Connections `/api/matching/connections/`

#### GET `/api/matching/connections/`
List all accepted connections with pagination.

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

**Response (200):**
```json
{
  "count": 30,
  "next": "http://localhost:8000/api/matching/connections/?page=2",
  "previous": null,
  "results": [
    {
      "id": 3,
      "user": {
        "id": 123,
        "email": "bob@example.com",
        "full_name": "Bob Smith",
        "avatar_url": "https://example.com/avatar2.jpg",
        "school": 1,
        "major": "Computer Science",
        "year": 3,
        "bio": "Hi there!"
      },
      "connection_state": "accepted",
      "accepted_at": "2025-10-24T10:05:00Z",
      "can_message": true,
      "conversation_id": 1
    }
  ]
}
```

#### GET `/api/matching/connections/{id}/`
Get details of a specific connection.

**Response (200):**
```json
{
  "id": 3,
  "user": {
    "id": 123,
    "email": "bob@example.com",
    "full_name": "Bob Smith",
    "avatar_url": "https://example.com/avatar2.jpg",
    "school": 1,
    "major": "Computer Science",
    "year": 3,
    "bio": "Hi there!"
  },
  "connection_state": "accepted",
  "accepted_at": "2025-10-24T10:05:00Z",
  "can_message": true,
  "conversation_id": 1
}
```

#### GET `/api/matching/connections/statistics/`
Get connection statistics for current user.

**Response (200):**
```json
{
  "sent_pending": 5,
  "received_pending": 3,
  "accepted_connections": 12,
  "total_requests": 8
}
```

#### GET `/api/matching/connections/status/{user_id}/`
Check connection status with another user.

**Response (200):**
```json
{
  "connected": true,
  "can_message": true,
  "user1_sent": true,
  "user2_sent": false,
  "user1_request_state": "accepted",
  "user2_request_state": null
}
```

---

## 💬 Chat `/api/chat/`

Real-time chat feature for accepted connections. Supports both REST API (for history) and WebSocket (for real-time messaging).

### Conversations `/api/chat/conversations/`

#### GET `/api/chat/conversations/by-connection/?connection_id={id}`
Get or create conversation by connection ID. Auto-creates if doesn't exist.

**Query Parameters:**
- `connection_id` (required) - Connection ID

**Response (200):**
```json
{
  "id": 1,
  "connection": 5,
  "participants": [...],
  "other_participant": {...},
  "last_message": {...},
  "unread_count": 0,
  "last_message_at": null,
  "created_at": "2025-10-25T10:00:00Z"
}
```

#### GET `/api/chat/conversations/`
List all conversations for current user.

**Response (200):**
```json
[
  {
    "id": 1,
    "other_participant": {
      "id": 2,
      "email": "user2@example.com",
      "full_name": "Jane Doe",
      "avatar_url": "https://example.com/avatar2.jpg"
    },
    "last_message_preview": {
      "content": "Hello! How are you?",
      "sender_id": 2,
      "created_at": "2025-10-25T10:00:00Z"
    },
    "last_message_at": "2025-10-25T10:00:00Z",
    "unread_count": 3
  }
]
```

#### GET `/api/chat/conversations/{id}/`
Get conversation details.

**Response (200):**
```json
{
  "id": 1,
  "connection": 5,
  "participants": [
    {
      "id": 1,
      "email": "user1@example.com",
      "full_name": "John Doe",
      "avatar_url": "https://example.com/avatar1.jpg"
    },
    {
      "id": 2,
      "email": "user2@example.com",
      "full_name": "Jane Doe",
      "avatar_url": "https://example.com/avatar2.jpg"
    }
  ],
  "other_participant": {
    "id": 2,
    "email": "user2@example.com",
    "full_name": "Jane Doe",
    "avatar_url": "https://example.com/avatar2.jpg"
  },
  "last_message": {
    "id": 123,
    "sender_id": 2,
    "sender_name": "Jane Doe",
    "content": "Hello!",
    "is_read": false,
    "created_at": "2025-10-25T10:00:00Z"
  },
  "unread_count": 3,
  "last_message_at": "2025-10-25T10:00:00Z",
  "created_at": "2025-10-24T08:00:00Z"
}
```

#### GET `/api/chat/conversations/{id}/messages/`
Get message history with pagination.

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Messages per page (default: 50)

**Response (200):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/chat/conversations/1/messages/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "sender_id": 1,
      "sender_name": "John Doe",
      "sender_avatar": "https://example.com/avatar1.jpg",
      "content": "Hello! How are you?",
      "is_read": true,
      "read_at": "2025-10-25T10:05:00Z",
      "created_at": "2025-10-25T10:00:00Z"
    }
  ]
}
```

#### POST `/api/chat/conversations/{id}/mark_read/`
Mark messages as read.

**Request:**
```json
{
  "message_ids": [123, 124, 125]
}
```
*Note: If `message_ids` not provided, marks all unread messages in conversation.*

**Response (200):**
```json
{
  "message": "Marked 3 message(s) as read",
  "marked_count": 3
}
```

### Messages `/api/chat/messages/`

#### POST `/api/chat/messages/`
Send a message (HTTP fallback).

**Request:**
```json
{
  "conversation": 1,
  "content": "Hello! How are you?"
}
```

**Response (201):**
```json
{
  "id": 123,
  "conversation": 1,
  "sender": {
    "id": 1,
    "email": "user1@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://example.com/avatar1.jpg"
  },
  "content": "Hello! How are you?",
  "read_at": null,
  "is_read": false,
  "created_at": "2025-10-25T10:00:00Z",
  "updated_at": "2025-10-25T10:00:00Z"
}
```

### WebSocket (Real-time)

**Connection URL:**
```
ws://localhost:8000/ws/chat/{conversation_id}/?token={access_token}
```

Or use Authorization header: `Authorization: Bearer {access_token}`

#### Events to Send (Client → Server)

**1. Send Message:**
```json
{
  "type": "chat_message",
  "content": "Hello!"
}
```

**2. Typing Indicator:**
```json
{
  "type": "typing_indicator",
  "is_typing": true
}
```

**3. Mark as Read:**
```json
{
  "type": "message_read",
  "message_ids": [123, 124]
}
```

#### Events to Receive (Server → Client)

**1. Connection Success:**
```json
{
  "type": "connection_established",
  "message": "Connected to chat"
}
```

**2. New Message:**
```json
{
  "type": "chat_message",
  "message_id": 123,
  "sender_id": 2,
  "sender_name": "Jane Doe",
  "sender_avatar": "https://example.com/avatar2.jpg",
  "content": "Hello!",
  "created_at": "2025-10-25T10:00:00Z"
}
```

**3. Typing Indicator:**
```json
{
  "type": "typing_indicator",
  "user_id": 2,
  "user_name": "Jane Doe",
  "is_typing": true
}
```

**4. Messages Read:**
```json
{
  "type": "messages_read",
  "user_id": 2,
  "message_ids": [123, 124],
  "read_at": "2025-10-25T10:05:00Z"
}
```

**5. Error:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

---

## 🏫 Schools `/api/schools/`

### GET `/api/schools/`
List schools with pagination and filters.

**Query Parameters:**
- `search` - Search by name, short_name, city, or address
- `city` - Filter by city name
- `lat`, `lng`, `radius` - Proximity search (radius in km, default: 10)
- `ordering` - Order by: name, city, created_at (prefix with - for descending)
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/schools/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Harvard University",
      "short_name": "Harvard",
      "city": 1,
      "student_count": 150
    }
  ]
}
```

### POST `/api/schools/`
Create a new school.

**Request:**
```json
{
  "name": "Harvard University",
  "short_name": "Harvard",
  "address": "Cambridge, MA",
  "city": 1,
  "latitude": 42.3744,
  "longitude": -71.1169,
  "website": "https://www.harvard.edu",
  "email": "info@harvard.edu",
  "phone": "+1-617-495-1000"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Harvard University",
  "short_name": "Harvard",
  "address": "Cambridge, MA",
  "city": 1,
  "website": "https://www.harvard.edu",
  "email": "info@harvard.edu",
  "phone": "+1-617-495-1000"
}
```

### GET `/api/schools/{id}/`
Get school details.

**Response (200):**
```json
{
  "id": 1,
  "name": "Harvard University",
  "short_name": "Harvard",
  "address": "Cambridge, MA",
  "city": 1,
  "latitude": 42.3744,
  "longitude": -71.1169,
  "website": "https://www.harvard.edu",
  "email": "info@harvard.edu",
  "phone": "+1-617-495-1000",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z",
  "student_count": 150
}
```

### PUT/PATCH `/api/schools/{id}/`
Update school information.

**Request:**
```json
{
  "name": "Harvard University - Updated",
  "website": "https://www.harvard.edu"
}
```

**Response (200):** Same structure as GET

### DELETE `/api/schools/{id}/`
Delete a school.

**Response (204):** No content

### GET `/api/schools/search/location/`
Search schools by geographic location.

**Query Parameters (required):**
- `lat` - Latitude
- `lng` - Longitude
- `radius` - Radius in km (default: 10)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Harvard University",
    "short_name": "Harvard",
    "address": "Cambridge, MA",
    "city": 1,
    "latitude": 42.3744,
    "longitude": -71.1169,
    "website": "https://www.harvard.edu",
    "email": "info@harvard.edu",
    "phone": "+1-617-495-1000",
    "created_at": "2025-10-20T10:00:00Z",
    "updated_at": "2025-10-24T10:00:00Z",
    "student_count": 150,
    "distance_km": 2.5
  }
]
```

### GET `/api/schools/search/city/`
List schools by city.

**Query Parameters (required):**
- `city` - City name

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Harvard University",
    "short_name": "Harvard",
    "city": 1,
    "student_count": 150
  }
]
```

---

## 🌆 Cities `/api/cities/`

### GET `/api/cities/`
List cities with pagination and filters.

**Query Parameters:**
- `search` - Search by name
- `lat`, `lng`, `radius` - Proximity search (radius in km, default: 50)
- `ordering` - Order by: name (prefix with - for descending)
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 30,
  "next": "http://localhost:8000/api/cities/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Boston",
      "school_count": 25
    }
  ]
}
```

### POST `/api/cities/`
Create a new city.

**Request:**
```json
{
  "name": "Boston",
  "latitude": 42.3601,
  "longitude": -71.0589
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Boston"
}
```

### GET `/api/cities/{id}/`
Get city details.

**Response (200):**
```json
{
  "id": 1,
  "name": "Boston",
  "latitude": 42.3601,
  "longitude": -71.0589,
  "school_count": 25
}
```

### PUT/PATCH `/api/cities/{id}/`
Update city information.

**Request:**
```json
{
  "name": "Boston - Updated"
}
```

**Response (200):** Same structure as GET

### DELETE `/api/cities/{id}/`
Delete a city.

**Response (204):** No content

### GET `/api/cities/search/location/`
Search cities by geographic location.

**Query Parameters (required):**
- `lat` - Latitude
- `lng` - Longitude
- `radius` - Radius in km (default: 50)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Boston",
    "latitude": 42.3601,
    "longitude": -71.0589,
    "school_count": 25,
    "distance_km": 5.2
  }
]
```

---

## 📚 Subjects `/api/subjects/`

### GET `/api/subjects/`
List subjects with pagination and filters.
  
**Query Parameters:**
- `search` - Search by code, name_vi, or name_en
- `level` - Filter by level (beginner, intermediate, advanced, expert)
- `ordering` - Order by: code, name_en, created_at (prefix with - for descending)
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/subjects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "CS101",
      "name_vi": "Lập trình cơ bản",
      "name_en": "Introduction to Programming",
      "level": "beginner",
      "user_count": 45
    }
  ]
}
```

### POST `/api/subjects/`
Create a new subject.

**Request:**
```json
{
  "code": "CS101",
  "name_vi": "Lập trình cơ bản",
  "name_en": "Introduction to Programming",
  "level": "beginner"
}
```

**Response (201):**
```json
{
  "code": "CS101",
  "name_vi": "Lập trình cơ bản",
  "name_en": "Introduction to Programming",
  "level": "beginner"
}
```

### GET `/api/subjects/{id}/`
Get subject details.

**Response (200):**
```json
{
  "id": 1,
  "code": "CS101",
  "name_vi": "Lập trình cơ bản",
  "name_en": "Introduction to Programming",
  "level": "beginner",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z",
  "user_count": 45,
  "learners_count": 30,
  "teachers_count": 15
}
```

### PUT/PATCH `/api/subjects/{id}/`
Update subject information.

**Request:**
```json
{
  "name_en": "Introduction to Programming - Updated",
  "level": "intermediate"
}
```

**Response (200):** Same structure as POST

### DELETE `/api/subjects/{id}/`
Delete a subject.

**Response (204):** No content

---

## 📖 User Subjects `/api/user-subjects/`

### GET `/api/user-subjects/`
List current user's subjects.

**Query Parameters:**
- `search` - Search by subject code, name_vi, or name_en
- `level` - Filter by user's level (beginner, intermediate, advanced, expert)
- `intent` - Filter by intent (learn, teach, both)
- `ordering` - Order by: level, intent, created_at (prefix with - for descending)
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "subject": 1,
      "subject_code": "CS101",
      "subject_name_en": "Introduction to Programming",
      "level": "intermediate",
      "intent": "learn"
    }
  ]
}
```

### POST `/api/user-subjects/`
Add a subject to user's learning list.

**Request:**
```json
{
  "subject": 1,
  "level": "intermediate",
  "intent": "learn",
  "note": "Studying for exam"
}
```

**Response (201):**
```json
{
  "subject": 1,
  "level": "intermediate",
  "intent": "learn",
  "note": "Studying for exam"
}
```

### GET `/api/user-subjects/{id}/`
Get user subject details.

**Response (200):**
```json
{
  "id": 1,
  "user": 1,
  "user_email": "user@example.com",
  "user_full_name": "John Doe",
  "subject": 1,
  "subject_code": "CS101",
  "subject_name_vi": "Lập trình cơ bản",
  "subject_name_en": "Introduction to Programming",
  "subject_level": "beginner",
  "level": "intermediate",
  "intent": "learn",
  "note": "Studying for exam",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z"
}
```

### PUT/PATCH `/api/user-subjects/{id}/`
Update user subject.

**Request:**
```json
{
  "level": "advanced",
  "note": "Preparing for final exam"
}
```

**Response (200):** Same structure as POST

### DELETE `/api/user-subjects/{id}/`
Remove subject from user's list.

**Response (204):** No content

---

## 🎯 Goals `/api/goals/`

### GET `/api/goals/`
List goals with pagination and filters.

**Query Parameters:**
- `search` - Search by code or name
- `type` - Filter by type (daily, weekly, monthly, yearly, milestone)
- `ordering` - Order by: code, name, type, created_at (prefix with - for descending)
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/goals/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "STUDY_HOURS",
      "name": "Study Hours Per Day",
      "type": "daily",
      "user_count": 120
    }
  ]
}
```

### POST `/api/goals/`
Create a new goal.

**Request:**
```json
{
  "code": "STUDY_HOURS",
  "name": "Study Hours Per Day",
  "type": "daily"
}
```

**Response (201):**
```json
{
  "code": "STUDY_HOURS",
  "name": "Study Hours Per Day",
  "type": "daily"
}
```

### GET `/api/goals/{id}/`
Get goal details.

**Response (200):**
```json
{
  "id": 1,
  "code": "STUDY_HOURS",
  "name": "Study Hours Per Day",
  "type": "daily",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z",
  "user_count": 120,
  "avg_target_value": 4.5
}
```

### PUT/PATCH `/api/goals/{id}/`
Update goal information.

**Request:**
```json
{
  "name": "Study Hours Per Day - Updated"
}
```

**Response (200):** Same structure as POST

### DELETE `/api/goals/{id}/`
Delete a goal.

**Response (204):** No content

---

## ✅ User Goals `/api/user-goals/`

### GET `/api/user-goals/`
List current user's goals.

**Query Parameters:**
- `search` - Search by goal code or name
- `type` - Filter by goal type (daily, weekly, monthly, yearly, milestone)
- `ordering` - Order by: target_value, target_date, created_at (prefix with - for descending)
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "goal": 1,
      "goal_code": "STUDY_HOURS",
      "goal_name": "Study Hours Per Day",
      "target_value": 5.0,
      "target_date": "2025-12-31"
    }
  ]
}
```

### POST `/api/user-goals/`
Add a goal to user's list.

**Request:**
```json
{
  "goal": 1,
  "target_value": 5.0,
  "target_date": "2025-12-31"
}
```

**Response (201):**
```json
{
  "goal": 1,
  "target_value": 5.0,
  "target_date": "2025-12-31"
}
```

### GET `/api/user-goals/{id}/`
Get user goal details.

**Response (200):**
```json
{
  "id": 1,
  "user": 1,
  "user_email": "user@example.com",
  "user_full_name": "John Doe",
  "goal": 1,
  "goal_code": "STUDY_HOURS",
  "goal_name": "Study Hours Per Day",
  "goal_type": "daily",
  "target_value": 5.0,
  "target_date": "2025-12-31",
  "created_at": "2025-10-20T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z"
}
```

### PUT/PATCH `/api/user-goals/{id}/`
Update user goal.

**Request:**
```json
{
  "target_value": 6.0,
  "target_date": "2025-12-31"
}
```

**Response (200):** Same structure as POST

### DELETE `/api/user-goals/{id}/`
Remove goal from user's list.

**Response (204):** No content

---

## Common Query Parameters

### Pagination (all list endpoints)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

### Common Filters
- **Schools**: `search`, `city`, `lat`, `lng`, `radius`, `ordering`
- **Cities**: `search`, `lat`, `lng`, `radius`, `ordering`
- **Subjects**: `search`, `level`, `ordering`
- **User Subjects**: `search`, `level`, `intent`, `ordering`
- **Goals**: `search`, `type`, `ordering`
- **User Goals**: `search`, `type`, `ordering`
- **Connection Requests**: `state` (pending, accepted, rejected, blocked), `page`, `page_size` (pagination)
- **Connections**: `page`, `page_size` (pagination)
- **Chat Messages**: `page`, `page_size` (pagination)
- **Conversations**: `page`, `page_size` (pagination)

---

## Important Notes

### Authentication
- All endpoints require JWT authentication except `/api/auth/register/` and `/api/auth/login/`
- JWT tokens have the following lifetimes:
  - Access token: 5 minutes (configurable)
  - Refresh token: 24 hours (configurable)
- Use refresh token to get new access token via `/api/auth/token/refresh/`

### Location Tracking
- Location is saved to history if:
  - User moved **more than 100 meters** OR
  - **More than 15 minutes** have passed since last update
- First location is always saved to history
- Current location is always updated in `User.geom_last_point`

### Discover Nearby Learners
- Excludes current user
- Excludes already connected users
- Excludes users with existing connection requests (any state)
- Uses user's `learning_radius_km` if radius parameter not specified
- Results ordered by distance (nearest first)

### Matching System

**Connection States:**
```
pending → accepted (can message immediately)
       ↘ rejected
       ↘ blocked
```

**Important Rules:**
- Connection is **immediately established** when request is accepted
- Messaging is enabled immediately after acceptance
- Only **sender** can cancel pending requests (DELETE)
- Only **receiver** can accept/reject pending requests
- **Both parties** can block at any state
- A user can only have **one connection request** with another user at a time
- Cannot send connection request to yourself

**Permissions:**
- Cancel request: Only sender, only pending state
- Accept/Reject: Only receiver, only pending state
- Block: Both sender and receiver, any state except blocked

### Chat System

**Real-time Messaging:**
- Chat available **only for accepted connections**
- Conversation is **auto-created** when connection is accepted
- Supports both **REST API** (message history) and **WebSocket** (real-time)

**WebSocket Connection:**
```
ws://localhost:8000/ws/chat/{conversation_id}/?token={access_token}
```

**Features:**
- Real-time message delivery
- Typing indicators
- Message read receipts
- Unread message count
- Message history pagination

**Authentication:**
- REST API: Standard JWT Bearer token in header
- WebSocket: Token in query string or Authorization header

**Permissions:**
- Only conversation participants can access
- Only users with accepted connections can message
- Messages cannot be edited or deleted

### Privacy Levels
- `open` - Anyone can view profile
- `friends_of_friends` - Only friends and their friends can view
- `private` - Only the user can view

### User Status
- `active` - Normal active user
- `banned` - User is banned
- `deleted` - User account deleted

### Geographic Data
- All geographic coordinates use **SRID 4326** (WGS 84)
- Latitude range: -90 to 90
- Longitude range: -180 to 180
- Distance calculations use PostGIS for accuracy
- Proximity searches use PostGIS GIST indexes for performance

### Caching
- Connection requests and connections are cached in Redis
- Cache TTL:
  - Connection requests: 5 minutes
  - User connections: 10 minutes
  - Accepted connections: 10 minutes
- Cache is invalidated automatically when connection state changes

### Error Responses

**400 Bad Request:**
```json
{
  "field_name": ["Error message"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error."
}
```

---

## Authentication

All endpoints require JWT authentication:

```
Authorization: Bearer <your_access_token>
```

For WebSockets, include token in query string:
```
ws://domain/ws/groups/5/chat/?token=<your_access_token>
```

---

## Interactive Documentation

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

*For detailed field descriptions and complete examples, visit `/api/docs/` after starting the server.*

## Study Sessions API

**Base URL:** `/api/sessions/`

### Key Features
- Create in-person, virtual, or hybrid study sessions
- Discover nearby sessions
- Join/leave sessions
- Check-in/check-out tracking
- Recurrence support (daily, weekly, monthly)

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions/` | List all sessions (with filters) |
| POST | `/api/sessions/` | Create new session |
| GET | `/api/sessions/{id}/` | Get session details |
| PUT/PATCH | `/api/sessions/{id}/` | Update session (host only) |
| DELETE | `/api/sessions/{id}/` | Cancel session (host only) |
| POST | `/api/sessions/{id}/join/` | Join a session |
| POST | `/api/sessions/{id}/leave/` | Leave a session |
| POST | `/api/sessions/{id}/check_in/` | Check in to session |
| POST | `/api/sessions/{id}/check_out/` | Check out of session |
| GET | `/api/sessions/{id}/participants/` | List participants |
| GET | `/api/sessions/my_sessions/` | User's sessions |
| GET | `/api/sessions/nearby/` | Find nearby sessions |

### Query Parameters for Listing

- `status`: `upcoming`, `in_progress`, `completed`, `cancelled`
- `session_type`: `in_person`, `virtual`, `hybrid`
- `subject`: Subject ID (integer)
- `time_filter`: `upcoming`, `past`

---

## Study Groups API

**Base URL:** `/api/groups/`

### Key Features
- Create persistent study groups
- Public, private, or invite-only groups
- Role-based permissions (admin, moderator, member)
- Group chat with WebSocket support
- Member management

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/groups/` | List all groups (with filters) |
| POST | `/api/groups/` | Create new group |
| GET | `/api/groups/{id}/` | Get group details |
| PUT/PATCH | `/api/groups/{id}/` | Update group (admin only) |
| DELETE | `/api/groups/{id}/` | Archive group (admin only) |
| POST | `/api/groups/{id}/join/` | Join/request to join |
| POST | `/api/groups/{id}/leave/` | Leave group |
| POST | `/api/groups/{id}/invite/` | Invite user (mod/admin) |
| GET | `/api/groups/{id}/members/` | List members |
| GET | `/api/groups/my_groups/` | User's groups |
| GET | `/api/groups/nearby/` | Find nearby groups |

### Group Membership Management

**Base URL:** `/api/groups/memberships/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/groups/memberships/{id}/` | Get membership details |
| PATCH | `/api/groups/memberships/{id}/role/` | Update role (admin) |
| POST | `/api/groups/memberships/{id}/accept/` | Accept join request (admin) |
| POST | `/api/groups/memberships/{id}/reject/` | Reject join request (admin) |
| POST | `/api/groups/memberships/{id}/remove/` | Remove member (admin) |

### Group Messages

**Base URL:** `/api/groups/{group_id}/messages/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/groups/{group_id}/messages/` | List messages |
| POST | `/api/groups/{group_id}/messages/` | Send message |
| POST | `/api/groups/{group_id}/messages/mark_read/` | Mark as read |

---

## WebSocket APIs

### Group Chat WebSocket

**URL:** `ws://your-domain/ws/groups/{group_id}/chat/?token={jwt_token}`

**Client → Server Messages:**

```json
// Send message
{"type": "chat_message", "content": "Hello!"}

// Typing indicator
{"type": "typing_indicator", "is_typing": true}

// Mark as read
{"type": "message_read", "message_ids": [1, 2, 3]}
```

**Server → Client Messages:**

```json
// New message
{
  "type": "chat_message",
  "message_id": 105,
  "sender_id": 10,
  "sender_name": "John Doe",
  "sender_avatar": "https://...",
  "content": "Hello!",
  "created_at": "2025-10-30T16:00:00Z"
}

// Typing indicator
{
  "type": "typing_indicator",
  "user_id": 10,
  "user_name": "John Doe",
  "is_typing": true
}

// Messages read
{
  "type": "messages_read",
  "user_id": 15,
  "message_ids": [1, 2, 3],
  "read_at": "2025-10-30T16:05:00Z"
}
```

---

## Quick Start Examples

### Create and Join a Study Session

```javascript
// Create session
const session = await fetch('/api/sessions/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Calculus Study Group',
    session_type: 'virtual',
    meeting_link: 'https://zoom.us/j/123',
    start_time: '2025-11-01T14:00:00Z',
    duration_minutes: 120
  })
}).then(r => r.json());

// Join session
await fetch(`/api/sessions/${session.id}/join/`, {
  method: 'POST',
  headers: {'Authorization': `Bearer ${token}`}
});
```

### Create and Manage a Study Group

```javascript
// Create group
const group = await fetch('/api/groups/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Machine Learning Club',
    description: 'Weekly ML discussions',
    privacy: 'public',
    subject_ids: [10, 11]
  })
}).then(r => r.json());

// Invite user
await fetch(`/api/groups/${group.id}/invite/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({user_id: 42})
});
```

### Connect to Group Chat

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws/groups/${groupId}/chat/?token=${token}`
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'chat_message') {
    console.log(`${data.sender_name}: ${data.content}`);
  }
};

// Send message
ws.send(JSON.stringify({
  type: 'chat_message',
  content: 'Hello everyone!'
}));
```
