# To-Do List

A robust to-do list application built with Flask, Jinja2, and MongoDB. Features user authentication, secure password storage, and persistent data storage.

## Features

- 🔐 **User Authentication**: Secure login and signup with password hashing
- ✅ **Task Management**: Add, complete, and delete tasks
- 📊 **Statistics**: Track active and completed tasks
- 💾 **MongoDB Storage**: Persistent data storage with MongoDB
- 🎨 **Modern UI**: Beautiful and responsive user interface
- 🔒 **Session Management**: Secure session-based authentication
- 👤 **User Isolation**: Each user has their own task list

## Getting Started

### Prerequisites

- Python 3.13 or higher
- `uv` package manager ([install uv](https://github.com/astral-sh/uv))
- MongoDB instance (local or MongoDB Atlas)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd to_do_list
```

2. Install dependencies:

```bash
uv sync
```

3. Set up environment variables:

```bash
cp example.env .env
# Edit .env with your configuration
```

### MongoDB Atlas (Cloud) Setup

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Get your connection string
4. Update `.env` with your Atlas URI:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Running the Application

```bash
# Using uv
uv run python main.py

# Or activate the virtual environment manually
source .venv/bin/activate  # On macOS/Linux
python main.py
```

The application will be available at `http://127.0.0.1:5000` by default.

### First Time Setup

1. Navigate to `http://127.0.0.1:5000`
2. Click "Sign up" to create a new account
3. Enter a username and password (minimum 4 characters)
4. Login with your credentials
5. Start adding tasks!

## Project Structure

```
to_do_list/
├── app/
│   └── storage.py      # MongoDB storage layer
├── templates/
│   ├── index.html      # Main application interface
│   ├── login.html      # Login page
│   └── signup.html     # Signup page
├── .venv/              # Virtual environment (auto-generated)
├── main.py             # Flask application entry point
├── pyproject.toml      # Project dependencies and configuration
├── uv.lock             # Lock file for dependencies
├── example.env         # Example environment variables
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Architecture

### Storage Layer

The application uses a separate storage module (`app/storage.py`) that provides:

- **User Management**: Create users, verify credentials, check existence
- **Task Operations**: Add, complete, delete tasks
- **Data Retrieval**: Get user tasks and statistics
- **Password Security**: Bcrypt hashing for password storage

### Database Schema

**Users Collection:**

```json
{
  "username": "string",
  "password": "hashed_bcrypt",
  "todos": [{"id": int, "text": "string", "created_at": datetime}],
  "completed": [{"id": int, "text": "string", "completed_at": datetime}],
  "created_at": datetime
}
```
