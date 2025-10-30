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

---

## 📅 Study Sessions `/api/sessions/`

Create, discover, and join study sessions - both in-person and virtual.

### Key Features
- Schedule in-person, virtual, or hybrid study sessions
- Location-based discovery of nearby sessions
- Join/leave sessions with participant tracking
- Check-in/check-out attendance system
- Recurrence support (daily, weekly, monthly)
- Host-only controls and permissions

### GET `/api/sessions/`
List study sessions with optional filters.

**Query Parameters:**
- `status` - Filter by status: `upcoming`, `in_progress`, `completed`, `cancelled`
- `session_type` - Filter by type: `in_person`, `virtual`, `hybrid`
- `subject` - Filter by subject ID
- `time_filter` - Filter by time: `upcoming`, `past`
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/sessions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Calculus Study Group",
      "description": "Reviewing chapters 5-7 for midterm",
      "host": {
        "id": 10,
        "email": "user@example.com",
        "full_name": "John Doe",
        "avatar_url": "https://...",
        "school": 5,
        "major": "Mathematics",
        "year": 3
      },
      "subject": {
        "id": 15,
        "code": "MATH101",
        "name_en": "Calculus I",
        "name_vi": "Giải tích I",
        "level": "intermediate"
      },
      "session_type": "hybrid",
      "location_name": "Library Room 301",
      "start_time": "2025-11-01T14:00:00Z",
      "end_time": "2025-11-01T16:00:00Z",
      "duration_minutes": 120,
      "participant_count": 5,
      "max_participants": 10,
      "is_full": false,
      "status": "upcoming",
      "is_host": false,
      "is_participant": true,
      "created_at": "2025-10-25T10:00:00Z"
    }
  ]
}
```

### POST `/api/sessions/`
Create a new study session.

**Request:**
```json
{
  "title": "Python Study Session",
  "description": "Learning Flask framework",
  "subject": 20,
  "session_type": "virtual",
  "meeting_link": "https://zoom.us/j/123456789",
  "start_time": "2025-11-05T18:00:00Z",
  "duration_minutes": 90,
  "max_participants": 15,
  "recurrence_pattern": "weekly",
  "recurrence_end_date": "2025-12-31"
}
```

**For in-person/hybrid sessions:**
```json
{
  "title": "Database Study Group",
  "description": "SQL practice",
  "subject": 25,
  "session_type": "in_person",
  "location_name": "Computer Lab A",
  "location_address": "123 Main St, Building 2",
  "latitude": 10.762622,
  "longitude": 106.660172,
  "start_time": "2025-11-05T14:00:00Z",
  "duration_minutes": 120
}
```

**Response (201):**
```json
{
  "id": 42,
  "title": "Python Study Session",
  "description": "Learning Flask framework",
  "host": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Alice",
    "avatar_url": "https://...",
    "school": 3,
    "major": "CS",
    "year": 2
  },
  "subject": {
    "id": 20,
    "code": "CS301",
    "name_en": "Web Development",
    "name_vi": "Phát triển Web",
    "level": "intermediate"
  },
  "session_type": "virtual",
  "meeting_link": "https://zoom.us/j/123456789",
  "start_time": "2025-11-05T18:00:00Z",
  "end_time": "2025-11-05T19:30:00Z",
  "duration_minutes": 90,
  "participant_count": 1,
  "max_participants": 15,
  "is_full": false,
  "status": "upcoming",
  "participants": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Alice"
      },
      "status": "registered",
      "check_in_time": null,
      "check_out_time": null,
      "duration_minutes": null,
      "notes": "",
      "joined_at": "2025-10-30T10:00:00Z"
    }
  ],
  "is_host": true,
  "is_participant": true,
  "can_join": false,
  "created_at": "2025-10-30T10:00:00Z",
  "updated_at": "2025-10-30T10:00:00Z"
}
```

### GET `/api/sessions/{id}/`
Get detailed session information.

**Response (200):** Same structure as POST response.

### PUT/PATCH `/api/sessions/{id}/`
Update session (host only).

**Request:** Same fields as POST, all optional for PATCH.

**Response (200):** Updated session object.

### DELETE `/api/sessions/{id}/`
Cancel session (host only).

**Response (200):**
```json
{
  "message": "Session cancelled successfully."
}
```

### POST `/api/sessions/{id}/join/`
Join a study session.

**Request:**
```json
{
  "notes": "Looking forward to this session!"
}
```

**Response (200):**
```json
{
  "id": 10,
  "user": {
    "id": 5,
    "email": "student@example.com",
    "full_name": "Bob"
  },
  "status": "registered",
  "check_in_time": null,
  "check_out_time": null,
  "duration_minutes": null,
  "notes": "Looking forward to this session!",
  "joined_at": "2025-10-30T11:00:00Z",
  "updated_at": "2025-10-30T11:00:00Z"
}
```

### POST `/api/sessions/{id}/leave/`
Leave a study session.

**Response (200):**
```json
{
  "message": "You have left the session."
}
```

### POST `/api/sessions/{id}/check_in/`
Check in to a session (marks attendance).

**Response (200):**
```json
{
  "id": 10,
  "user": {
    "id": 5,
    "email": "student@example.com",
    "full_name": "Bob"
  },
  "status": "attended",
  "check_in_time": "2025-11-01T14:05:00Z",
  "check_out_time": null,
  "duration_minutes": null,
  "notes": "",
  "joined_at": "2025-10-30T11:00:00Z",
  "updated_at": "2025-11-01T14:05:00Z"
}
```

### POST `/api/sessions/{id}/check_out/`
Check out of a session (records study duration).

**Response (200):**
```json
{
  "id": 10,
  "user": {
    "id": 5,
    "email": "student@example.com",
    "full_name": "Bob"
  },
  "status": "attended",
  "check_in_time": "2025-11-01T14:05:00Z",
  "check_out_time": "2025-11-01T16:00:00Z",
  "duration_minutes": 115,
  "notes": "",
  "joined_at": "2025-10-30T11:00:00Z",
  "updated_at": "2025-11-01T16:00:00Z"
}
```

### GET `/api/sessions/{id}/participants/`
List all participants of a session.

**Response (200):**
```json
[
  {
    "id": 10,
    "user": {
      "id": 5,
      "email": "student@example.com",
      "full_name": "Bob",
      "avatar_url": "https://...",
      "school": 3,
      "major": "CS",
      "year": 2
    },
    "status": "attended",
    "check_in_time": "2025-11-01T14:05:00Z",
    "check_out_time": "2025-11-01T16:00:00Z",
    "duration_minutes": 115,
    "notes": "",
    "joined_at": "2025-10-30T11:00:00Z",
    "updated_at": "2025-11-01T16:00:00Z"
  }
]
```

### GET `/api/sessions/my_sessions/`
List user's sessions (hosting or attending).

**Query Parameters:**
- `role` - Filter by role: `hosting`, `attending` (default: both)

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Calculus Study Group",
    "description": "Reviewing chapters 5-7",
    "host": { /* host user object */ },
    "subject": { /* subject object */ },
    "session_type": "hybrid",
    "location_name": "Library Room 301",
    "start_time": "2025-11-01T14:00:00Z",
    "end_time": "2025-11-01T16:00:00Z",
    "duration_minutes": 120,
    "participant_count": 5,
    "max_participants": 10,
    "is_full": false,
    "status": "upcoming",
    "is_host": true,
    "is_participant": true,
    "created_at": "2025-10-25T10:00:00Z"
  }
]
```

### GET `/api/sessions/nearby/`
Find nearby in-person study sessions.

**Query Parameters:**
- `radius_km` - Search radius in km (default: 5)
- `session_type` - Filter by type

**Response (200):** Array of session objects, sorted by distance.

**Note:** Requires user location to be set.

---

## 👥 Study Groups `/api/groups/`

Create and manage persistent learning communities.

### Key Features
- Create public, private, or invite-only groups
- Role-based permissions (admin, moderator, member)
- Member management (invite, accept, promote, remove)
- Real-time group chat via WebSocket
- Location-based group discovery
- Subject associations

### GET `/api/groups/`
List study groups with optional filters.

**Query Parameters:**
- `status` - Filter by status: `active`, `inactive`, `archived`
- `privacy` - Filter by privacy: `public`, `private`, `invite_only`
- `subject` - Filter by subject ID
- `school` - Filter by school ID
- `page`, `page_size` - Pagination

**Response (200):**
```json
{
  "count": 30,
  "next": "http://localhost:8000/api/groups/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Machine Learning Study Group",
      "description": "Weekly discussions on ML algorithms",
      "avatar_url": "https://...",
      "created_by": {
        "id": 5,
        "email": "admin@example.com",
        "full_name": "Jane Smith",
        "avatar_url": "https://...",
        "school": 3,
        "major": "Computer Science",
        "year": 4
      },
      "school": {
        "id": 3,
        "name": "Tech University",
        "short_name": "TechU"
      },
      "subjects": [
        {
          "id": 25,
          "code": "CS401",
          "name_en": "Machine Learning",
          "name_vi": "Học máy",
          "level": "advanced"
        }
      ],
      "privacy": "public",
      "member_count": 12,
      "max_members": 20,
      "is_full": false,
      "status": "active",
      "is_member": true,
      "is_admin": false,
      "created_at": "2025-09-15T10:00:00Z"
    }
  ]
}
```

### POST `/api/groups/`
Create a new study group.

**Request:**
```json
{
  "name": "Data Structures Study Group",
  "description": "Collaborative learning for CS201",
  "avatar_url": "https://...",
  "school": 3,
  "subject_ids": [15, 16, 17],
  "privacy": "public",
  "max_members": 25,
  "latitude": 10.762622,
  "longitude": 106.660172
}
```

**Response (201):**
```json
{
  "id": 50,
  "name": "Data Structures Study Group",
  "description": "Collaborative learning for CS201",
  "avatar_url": "https://...",
  "created_by": { /* creator user object */ },
  "school": { /* school object */ },
  "geom_point": {
    "type": "Point",
    "coordinates": [106.660172, 10.762622]
  },
  "subjects": [ /* array of subject objects */ ],
  "privacy": "public",
  "max_members": 25,
  "member_count": 1,
  "is_full": false,
  "status": "active",
  "memberships": [
    {
      "id": 1,
      "user": { /* creator user object */ },
      "role": "admin",
      "status": "active",
      "invited_by": null,
      "joined_at": "2025-10-30T12:00:00Z",
      "updated_at": "2025-10-30T12:00:00Z",
      "left_at": null
    }
  ],
  "is_member": true,
  "is_admin": true,
  "is_moderator": true,
  "can_join": false,
  "user_membership": { /* current user's membership */ },
  "created_at": "2025-10-30T12:00:00Z",
  "updated_at": "2025-10-30T12:00:00Z"
}
```

### GET `/api/groups/{id}/`
Get detailed group information.

**Response (200):** Same structure as POST response.

### PUT/PATCH `/api/groups/{id}/`
Update group (admin only).

**Request:** Same fields as POST, all optional for PATCH.

**Response (200):** Updated group object.

### DELETE `/api/groups/{id}/`
Archive group (admin only).

**Response (200):**
```json
{
  "message": "Group archived successfully."
}
```

### POST `/api/groups/{id}/join/`
Join or request to join a group.

**Behavior depends on privacy setting:**
- **Public**: Immediately joins
- **Private**: Creates pending request (requires admin approval)
- **Invite Only**: Only works if user has pending invitation

**Response (200):**
```json
{
  "message": "You have joined the group.",
  "membership": {
    "id": 25,
    "user": { /* user object */ },
    "role": "member",
    "status": "active",
    "invited_by": null,
    "joined_at": "2025-10-30T13:00:00Z",
    "updated_at": "2025-10-30T13:00:00Z",
    "left_at": null
  }
}
```

### POST `/api/groups/{id}/leave/`
Leave a group.

**Response (200):**
```json
{
  "message": "You have left the group."
}
```

**Note:** Cannot leave if you're the last admin. Promote someone else first.

### POST `/api/groups/{id}/invite/`
Invite a user to join the group (admin/moderator only).

**Request:**
```json
{
  "user_id": 42
}
```

**Response (200):**
```json
{
  "id": 30,
  "user": { /* invited user object */ },
  "role": "member",
  "status": "invited",
  "invited_by": { /* inviter user object */ },
  "joined_at": "2025-10-30T14:00:00Z",
  "updated_at": "2025-10-30T14:00:00Z",
  "left_at": null
}
```

### GET `/api/groups/{id}/members/`
List all group members.

**Response (200):**
```json
[
  {
    "id": 1,
    "user": {
      "id": 5,
      "email": "member@example.com",
      "full_name": "John Doe",
      "avatar_url": "https://...",
      "school": 3,
      "major": "CS",
      "year": 2
    },
    "role": "admin",
    "status": "active",
    "invited_by": null,
    "joined_at": "2025-09-15T10:00:00Z",
    "updated_at": "2025-09-15T10:00:00Z",
    "left_at": null
  }
]
```

**Note:** Non-members only see active members. Members see all memberships including pending.

### GET `/api/groups/my_groups/`
List groups the current user is a member of.

**Response (200):** Array of group objects.

### GET `/api/groups/nearby/`
Find nearby study groups.

**Query Parameters:**
- `radius_km` - Search radius in km (default: 10)
- `subject` - Filter by subject ID

**Response (200):** Array of group objects, sorted by distance.

**Note:** Requires user location to be set.

---

## 🔧 Group Membership Management `/api/groups/memberships/`

Manage group memberships and roles.

### GET `/api/groups/memberships/{id}/`
Get membership details.

**Response (200):**
```json
{
  "id": 1,
  "group": { /* group object */ },
  "user": { /* user object */ },
  "role": "moderator",
  "status": "active",
  "invited_by": { /* inviter user object */ },
  "joined_at": "2025-09-15T10:00:00Z",
  "updated_at": "2025-10-15T10:00:00Z",
  "left_at": null
}
```

### PATCH `/api/groups/memberships/{id}/role/`
Update member's role (admin only).

**Request:**
```json
{
  "role": "moderator"
}
```

**Roles:** `admin`, `moderator`, `member`

**Response (200):** Updated membership object.

**Note:** Cannot demote the last admin.

### POST `/api/groups/memberships/{id}/accept/`
Accept a join request (admin only).

**Response (200):** Membership object with status="active".

### POST `/api/groups/memberships/{id}/reject/`
Reject a join request (admin only).

**Response (200):**
```json
{
  "message": "Join request rejected."
}
```

### POST `/api/groups/memberships/{id}/remove/`
Remove a member from group (admin only).

**Response (200):**
```json
{
  "message": "Member removed from group."
}
```

**Note:** Cannot remove the last admin.

---

## 💬 Group Messages `/api/groups/{group_id}/messages/`

Send and receive messages in group conversations.

### GET `/api/groups/{group_id}/messages/`
List group messages with pagination.

**Response (200):**
```json
[
  {
    "id": 100,
    "conversation": 5,
    "sender": {
      "id": 10,
      "email": "user@example.com",
      "full_name": "John Doe",
      "avatar_url": "https://...",
      "school": 3,
      "major": "CS",
      "year": 2
    },
    "content": "Hey everyone, let's meet tomorrow!",
    "is_read": true,
    "created_at": "2025-10-30T15:00:00Z"
  }
]
```

### POST `/api/groups/{group_id}/messages/`
Send a message to the group.

**Request:**
```json
{
  "content": "Sounds good! I'll be there."
}
```

**Response (201):** Message object.

### POST `/api/groups/{group_id}/messages/mark_read/`
Mark messages as read.

**Request:**
```json
{
  "message_ids": [100, 101, 102]
}
```

**Response (200):**
```json
{
  "message": "3 messages marked as read."
}
```

---

## 🔌 Group Chat WebSocket

Real-time messaging for study groups.

### Connection
```
ws://localhost:8000/ws/groups/{group_id}/chat/?token={access_token}
```

Or use Authorization header: `Authorization: Bearer {access_token}`

### Events to Send (Client → Server)

**1. Send Message:**
```json
{
  "type": "chat_message",
  "content": "Hello everyone!"
}
```

**2. Typing Indicator:**
```json
{
  "type": "typing_indicator",
  "is_typing": true
}
```

**3. Mark Messages as Read:**
```json
{
  "type": "message_read",
  "message_ids": [100, 101, 102]
}
```

### Events to Receive (Server → Client)

**1. Connection Established:**
```json
{
  "type": "connection_established",
  "message": "Connected to group chat"
}
```

**2. Chat Message:**
```json
{
  "type": "chat_message",
  "message_id": 105,
  "sender_id": 10,
  "sender_name": "John Doe",
  "sender_avatar": "https://...",
  "content": "Hello everyone!",
  "created_at": "2025-10-30T16:00:00Z"
}
```

**3. Typing Indicator:**
```json
{
  "type": "typing_indicator",
  "user_id": 10,
  "user_name": "John Doe",
  "is_typing": true
}
```

**4. Messages Read:**
```json
{
  "type": "messages_read",
  "user_id": 15,
  "message_ids": [100, 101, 102],
  "read_at": "2025-10-30T16:05:00Z"
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

## 🚀 Quick Start Examples

### Example 1: Create and Join a Study Session

```javascript
// 1. Create a virtual study session
const session = await fetch('/api/sessions/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'JavaScript Fundamentals',
    description: 'Learning async/await and promises',
    subject: 30,
    session_type: 'virtual',
    meeting_link: 'https://meet.google.com/abc-defg-hij',
    start_time: '2025-11-10T19:00:00Z',
    duration_minutes: 120,
    max_participants: 8
  })
}).then(r => r.json());

// 2. Find nearby in-person sessions
const nearbySessions = await fetch(
  '/api/sessions/nearby/?radius_km=3&session_type=in_person',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
).then(r => r.json());

// 3. Join a session
await fetch(`/api/sessions/${sessionId}/join/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ notes: 'Excited to learn!' })
});

// 4. Check in to session
await fetch(`/api/sessions/${sessionId}/check_in/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Example 2: Create and Manage a Study Group

```javascript
// 1. Create a study group
const group = await fetch('/api/groups/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Algorithms & Data Structures',
    description: 'Weekly problem-solving sessions',
    subject_ids: [20, 21],
    privacy: 'public',
    max_members: 15
  })
}).then(r => r.json());

// 2. Join a group
await fetch(`/api/groups/${groupId}/join/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

// 3. Invite a user (admin/moderator only)
await fetch(`/api/groups/${groupId}/invite/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ user_id: 42 })
});

// 4. Promote member to moderator (admin only)
await fetch(`/api/groups/memberships/${membershipId}/role/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ role: 'moderator' })
});
```

### Example 3: Connect to Group Chat WebSocket

```javascript
// Connect to group chat
const ws = new WebSocket(
  `ws://localhost:8000/ws/groups/${groupId}/chat/?token=${token}`
);

ws.onopen = () => {
  console.log('Connected to group chat');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case 'connection_established':
      console.log('Connection established');
      break;

    case 'chat_message':
      console.log(`${data.sender_name}: ${data.content}`);
      displayMessage(data);
      break;

    case 'typing_indicator':
      if (data.is_typing) {
        showTypingIndicator(data.user_name);
      } else {
        hideTypingIndicator(data.user_name);
      }
      break;

    case 'messages_read':
      updateReadReceipts(data.message_ids, data.user_id);
      break;

    case 'error':
      console.error('WebSocket error:', data.message);
      break;
  }
};

// Send a message
const sendMessage = (content) => {
  ws.send(JSON.stringify({
    type: 'chat_message',
    content: content
  }));
};

// Send typing indicator
const sendTypingIndicator = (isTyping) => {
  ws.send(JSON.stringify({
    type: 'typing_indicator',
    is_typing: isTyping
  }));
};

// Mark messages as read
const markMessagesRead = (messageIds) => {
  ws.send(JSON.stringify({
    type: 'message_read',
    message_ids: messageIds
  }));
};
```

---

## 📝 Additional Notes

### Study Sessions

**Session States:**
- `upcoming` - Session hasn't started yet
- `in_progress` - Session is currently active
- `completed` - Session has ended
- `cancelled` - Session was cancelled by host

**Participant States:**
- `registered` - Signed up but not checked in
- `attended` - Checked in (may or may not have checked out)
- `no_show` - Registered but didn't attend
- `cancelled` - Participant cancelled their registration

**Permissions:**
- Host can update/cancel session
- Participants can leave anytime before check-in
- Check-in available only for registered participants
- Check-out available only for checked-in participants

**Recurrence:**
- Sessions can repeat daily, weekly, or monthly
- Requires recurrence_end_date when pattern is set
- Future: Individual recurring instances can be managed separately

### Study Groups

**Privacy Levels:**
- `public` - Anyone can see and join immediately
- `private` - Anyone can see, but joining requires admin approval
- `invite_only` - Only visible to members, invitation required to join

**Member Roles:**
- `admin` - Full control (can do everything)
- `moderator` - Can manage members and invite users
- `member` - Regular member with basic permissions

**Membership States:**
- `active` - Active member
- `pending` - Requested to join (awaiting approval)
- `invited` - Invited by admin (awaiting acceptance)
- `removed` - Removed from group by admin
- `left` - User left the group voluntarily

**Important Rules:**
- At least one admin must exist at all times
- Cannot remove or demote the last admin
- Group creator automatically becomes admin
- Group conversation auto-created on group creation
- Only active members can access group chat

---

*Last Updated: 2025-10-30*
*For interactive API testing, visit: http://localhost:8000/api/docs/*
