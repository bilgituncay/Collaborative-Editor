# Real-Time Collaborative Code Editor

A feature-rich, real-time collaborative code editor built with Django and WebSockets. Multiple users can simultaneously edit documents with live cursor tracking, syntax highlighting, and granular permission controls.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![WebSocket](https://img.shields.io/badge/WebSocket-Channels-orange)

## Features

### 🚀 Real-Time Collaboration
- **Live Editing**: See changes from other users in real-time as they type
- **Cursor Tracking**: View collaborators' cursor positions with color-coded indicators
- **User Presence**: Know who's currently viewing or editing the document
- **Auto-Reconnection**: Automatic WebSocket reconnection on network interruptions

### 👥 User Management & Permissions
- **User Authentication**: Secure registration and login system
- **Document Ownership**: Create and manage your own documents
- **Collaboration Invites**: Search and invite users by username or email
- **Permission Levels**:
  - **Owner**: Full control over document and collaborators
  - **Can Edit**: Read and write access to document content
  - **View Only**: Read-only access to documents

### 💻 Code Editor Features
- **Syntax Highlighting**: Support for 10+ programming languages
  - Python, JavaScript, Java, C++, Go, Rust, Ruby, PHP, HTML, CSS
- **Code-Aware Features**:
  - Line numbers
  - Bracket matching
  - Auto-closing brackets
  - Active line highlighting
  - Monokai dark theme

### 📄 Document Management
- **Document List**: Organized view of owned and shared documents
- **Shared With Me**: Separate section for documents you collaborate on
- **Collaborator Count**: See how many people have access to each document
- **Document Deletion**: Safe deletion with confirmation dialog
- **Version Tracking**: Database-backed document versions (ready for future implementation)

## Technology Stack

**Backend:**
- Django 5.2 - Web framework
- Django Channels - WebSocket support
- Redis - Channel layer backend (or in-memory for development)
- SQLite - Database (easily switchable to PostgreSQL)

**Frontend:**
- CodeMirror 5.65 - Code editor component
- Vanilla JavaScript - Real-time synchronization logic
- CSS3 - Modern, responsive styling

## Prerequisites

- Python 3.10+
- Redis (optional, can use in-memory channels)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd collaborative_editor
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install Django channels channels-redis redis daphne whitenoise
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Running the Application

### Option 1: With Redis (Recommended)

**Start Redis:**

```bash
# Windows (using Docker)
docker run -d -p 6379:6379 --name redis redis:latest

# Linux/Mac
redis-server

# WSL
sudo service redis-server start
```

**Run the server:**

```bash
# Windows
run_server.bat

# Linux/Mac
export DJANGO_SETTINGS_MODULE=collaborative_editor.settings
daphne -b 0.0.0.0 -p 8000 collaborative_editor.asgi:application
```

### Option 2: Without Redis (Development Only)

Update `settings.py`:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

Then run:

```bash
daphne -b 0.0.0.0 -p 8000 collaborative_editor.asgi:application
```

**Access the application at:** `http://localhost:8000`

## Usage Guide

### Getting Started

1. **Register an Account**
   - Navigate to `http://localhost:8000/register/`
   - Fill in username, email, and password
   - You'll be automatically logged in

2. **Create a Document**
   - Click "+ New Document" on the dashboard
   - Choose a title and programming language
   - Click "Create Document"

3. **Invite Collaborators**
   - Open a document you own
   - Click "👥 Manage Collaborators"
   - Search for users by username or email
   - Select permission level (View Only or Can Edit)
   - Click "Add"

4. **Collaborate in Real-Time**
   - Share the document with team members
   - See live cursor positions and edits
   - View connection status in the header
   - Edit simultaneously without conflicts

### Keyboard Shortcuts

- `Tab` - Insert 4 spaces
- `Ctrl+Z` / `Cmd+Z` - Undo
- `Ctrl+Y` / `Cmd+Y` - Redo
- `Ctrl+F` / `Cmd+F` - Find
- `Ctrl+A` / `Cmd+A` - Select all

## Project Structure

```
collaborative_editor/
├── collaborative_editor/      # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.
