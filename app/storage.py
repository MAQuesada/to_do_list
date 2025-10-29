"""
Storage Module for MongoDB Operations

This module provides a Storage class for managing user data and todo tasks
in MongoDB database.
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime
from typing import Optional, List, Dict

load_dotenv()


class Storage:
    """Storage class for MongoDB operations related to users and tasks."""

    def __init__(self):
        """Initialize MongoDB connection."""
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = None
        self.db = None
        self.users_collection = None
        self.connect()

    def connect(self):
        """Establish connection to MongoDB."""
        try:
            # Create a new client and connect to the server
            self.client = MongoClient(self.mongodb_uri, server_api=ServerApi("1"))

            # Send a ping to confirm a successful connection
            self.client.admin.command("ping")
            print("Successfully connected to MongoDB!")

            # Get database and collections
            self.db = self.client.todo_app
            self.users_collection = self.db.users

            # Create unique index on username
            self.users_collection.create_index("username", unique=True)

        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

    def user_exists(self, username: str) -> bool:
        """Check if a user exists in the database."""
        return self.users_collection.find_one({"username": username}) is not None

    def create_user(self, username: str, password: str) -> bool:
        """
        Create a new user in the database.

        Args:
            username: The username
            password: The plain text password

        Returns:
            True if user was created successfully, False if user already exists
        """
        if self.user_exists(username):
            return False

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Create user document
        user_doc = {
            "username": username,
            "password": hashed_password,
            "todos": [],
            "completed": [],
            "created_at": datetime.utcnow(),
        }

        try:
            self.users_collection.insert_one(user_doc)
            return True
        except DuplicateKeyError:
            return False

    def verify_user(self, username: str, password: str) -> bool:
        """
        Verify user credentials.

        Args:
            username: The username
            password: The plain text password

        Returns:
            True if credentials are valid, False otherwise
        """
        user = self.users_collection.find_one({"username": username})

        if user is None:
            return False

        # Verify password
        return bcrypt.checkpw(password.encode("utf-8"), user["password"])

    def get_user_todos(self, username: str) -> List[Dict]:
        """
        Get all todo tasks for a user.

        Args:
            username: The username

        Returns:
            List of todo dictionaries
        """
        user = self.users_collection.find_one({"username": username})
        if user:
            return user.get("todos", [])
        return []

    def get_user_completed(self, username: str) -> List[Dict]:
        """
        Get all completed tasks for a user.

        Args:
            username: The username

        Returns:
            List of completed task dictionaries
        """
        user = self.users_collection.find_one({"username": username})
        if user:
            return user.get("completed", [])
        return []

    def add_todo(self, username: str, task_text: str) -> Dict:
        """
        Add a new todo task for a user.

        Args:
            username: The username
            task_text: The task description

        Returns:
            The created task dictionary
        """
        user = self.users_collection.find_one({"username": username})
        if not user:
            return None

        # Get current todos to determine next ID
        todos = user.get("todos", [])
        task_id = max([t.get("id", 0) for t in todos], default=0) + 1

        # Create new task
        new_task = {"id": task_id, "text": task_text, "created_at": datetime.utcnow()}

        # Add to todos array
        self.users_collection.update_one(
            {"username": username}, {"$push": {"todos": new_task}}
        )

        return new_task

    def complete_task(self, username: str, task_id: int) -> bool:
        """
        Move a task from todos to completed.

        Args:
            username: The username
            task_id: The task ID

        Returns:
            True if task was moved successfully, False otherwise
        """
        user = self.users_collection.find_one({"username": username})
        if not user:
            return False

        todos = user.get("todos", [])
        task_to_complete = None

        # Find the task
        for task in todos:
            if task.get("id") == task_id:
                task_to_complete = task
                break

        if not task_to_complete:
            return False

        # Remove from todos and add to completed
        self.users_collection.update_one(
            {"username": username},
            {
                "$pull": {"todos": {"id": task_id}},
                "$push": {
                    "completed": {**task_to_complete, "completed_at": datetime.utcnow()}
                },
            },
        )

        return True

    def delete_task(
        self, username: str, task_id: int, task_type: str = "todos"
    ) -> bool:
        """
        Delete a task from todos or completed.

        Args:
            username: The username
            task_id: The task ID
            task_type: Either "todos" or "completed"

        Returns:
            True if task was deleted successfully, False otherwise
        """
        result = self.users_collection.update_one(
            {"username": username}, {"$pull": {task_type: {"id": task_id}}}
        )

        return result.modified_count > 0

    def get_user_stats(self, username: str) -> Dict:
        """
        Get statistics for a user.

        Args:
            username: The username

        Returns:
            Dictionary with todo_count and completed_count
        """
        user = self.users_collection.find_one({"username": username})
        if not user:
            return {"todo_count": 0, "completed_count": 0}

        return {
            "todo_count": len(user.get("todos", [])),
            "completed_count": len(user.get("completed", [])),
        }
