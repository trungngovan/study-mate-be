# Study Mate API Documentation

## New Features: Study Sessions & Study Groups

This document provides comprehensive API documentation for the new Study Sessions and Study Groups features.

---

## Table of Contents

1. [Study Sessions API](#study-sessions-api)
2. [Study Groups API](#study-groups-api)
3. [WebSocket APIs](#websocket-apis)
4. [Quick Start Examples](#quick-start-examples)

---

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
