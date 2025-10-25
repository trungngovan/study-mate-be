# StudyMate Backend API

> **StudyMate** – A learning connection platform that helps you find study buddies near you

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io/)

## 📋 Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)

## 🎯 Introduction

**StudyMate** is an intelligent learning connection platform that helps students find and connect with study partners who share similar subjects, goals, and geographic proximity. The application provides:

- 🔍 Find study buddies based on geographic location
- 🤝 Connection system with friend requests
- 💬 Real-time messaging with WebSocket
- 📚 Subject and learning goal management
- 🏫 School and city management
- 🎯 Personal progress and goal tracking

## ✨ Key Features

### 🔐 Authentication & User Management
- Register/Login with JWT Authentication
- User profile management
- Password change
- Token refresh mechanism

### 📍 Location & Discovery
- Real-time user location updates
- Location history with PostGIS
- Find nearby learners within custom radius
- Optimized with GIST indexes

### 🤝 Connection System
- Send/Receive connection requests
- Accept/Reject requests
- Block users
- Manage connection list
- Redis caching for performance optimization

### 💬 Real-time Chat
- WebSocket for instant messaging
- Typing indicators
- Read receipts
- Message history with pagination
- Unread message count

### 🏫 Data Management
- CRUD operations for Schools/Cities
- CRUD operations for Subjects/Goals
- Personal subject management (UserSubject)
- Personal goal management (UserGoal)
- Geographic location search

## 🛠 Tech Stack

### Backend Framework
- **Django 4.2+** - Main web framework
- **Django REST Framework** - RESTful API
- **Django Channels** - WebSocket support
- **Simple JWT** - JWT Authentication

### Database
- **PostgreSQL 15+** - Primary database
- **PostGIS** - Geographic queries
- **Redis 7+** - Caching & WebSocket channels

### Key Libraries
- **drf-spectacular** - OpenAPI/Swagger documentation
- **django-cors-headers** - CORS support
- **channels-redis** - WebSocket channel layers
- **psycopg2** - PostgreSQL adapter

## 📦 System Requirements

- Python 3.11 or higher
- PostgreSQL 15+ with PostGIS extension
- Redis 7+
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone repository

```bash
git clone <repository-url>
cd study-mate-be
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install PostgreSQL and PostGIS

**macOS (Homebrew):**
```bash
brew install postgresql@15 postgis
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-15 postgresql-15-postgis-3
sudo systemctl start postgresql
```

### 5. Create database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE studymate_db;

# Connect to the database
\c studymate_db

# Enable PostGIS extension
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

# Exit
\q
```

### 6. Install Redis

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

## ⚙️ Configuration

### 1. Create `.env` file

Create a `.env` file in the root directory from `.env.template` and update the values with your own.

### 2. Run migrations

```bash
python manage.py migrate
```

### 3. Create superuser

```bash
python manage.py createsuperuser
```

## 🏃 Running the Application

### Development Server

**Run Django server:**
```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

### Run with WebSocket support

If you need WebSocket for chat:

```bash
# Ensure Redis is running
redis-cli ping  # Should return "PONG"

# Run Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

## 📚 API Documentation

### Interactive Documentation

After running the server, access these links:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

### Documentation File

For complete details about API endpoints, request/response formats, see: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## 📁 Project Structure

```
study-mate-be/
├── auth/                       # Authentication & Authorization
│   ├── authentication.py       # JWT authentication classes
│   ├── backends.py            # Custom authentication backends
│   ├── middleware.py          # Auth middleware
│   ├── permissions.py         # Custom permissions
│   ├── serializers.py         # Auth serializers
│   └── views.py               # Auth endpoints
│
├── users/                      # User management
│   ├── models.py              # User model
│   ├── serializers.py         # User serializers
│   ├── services.py            # Business logic
│   ├── views.py               # User endpoints
│   └── discover_urls.py       # Discovery endpoints
│
├── locations/                  # Location tracking
│   ├── models/
│   │   ├── cities.py          # City model
│   │   ├── schools.py         # School model
│   │   └── location_histories.py  # Location history
│   ├── serializers/
│   ├── views/
│   └── migrations/
│
├── matching/                   # Connection system
│   ├── models.py              # ConnectionRequest model
│   ├── serializers.py         # Matching serializers
│   ├── services.py            # Matching business logic
│   ├── views.py               # Matching endpoints
│   └── migrations/
│
├── chat/                       # Real-time chat
│   ├── models.py              # Conversation & Message models
│   ├── consumers.py           # WebSocket consumers
│   ├── routing.py             # WebSocket routing
│   ├── serializers.py         # Chat serializers
│   ├── services.py            # Chat business logic
│   ├── views.py               # Chat REST endpoints
│   └── management/commands/   # Management commands
│
├── learning/                   # Learning management
│   ├── models.py              # Subject, Goal models
│   ├── serializers/
│   │   ├── subjects.py
│   │   └── goals.py
│   ├── views/
│   │   ├── subjects.py
│   │   └── goals.py
│   └── migrations/
│
├── core/                       # Project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL configuration
│   ├── asgi.py                # ASGI config (WebSocket)
│   └── wsgi.py                # WSGI config
│
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── API_DOCUMENTATION.md        # Detailed API docs
└── README.md                   # This file
```

## 🚢 Deployment

Coming soon...

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.


## 🙏 Acknowledgments

- Django & Django REST Framework communities
- PostGIS for powerful geographic queries
- Channels for WebSocket support

## 📞 Support

For questions or issues, please open an issue on GitHub.

---

**Happy Learning! 🎓📚**
