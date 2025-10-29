"""
To-Do List Application

A Flask application for managing personal tasks with user authentication
and MongoDB storage.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from app.storage import Storage

app = Flask(__name__)

# Load secret key from environment variable
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize storage
storage = Storage()


@app.before_request
def require_login():
    """Check if user is logged in before accessing protected routes."""
    if (
        request.endpoint not in ["login", "signup", "static"]
        and "username" not in session
    ):
        return redirect(url_for("login"))


@app.route("/")
def index():
    """Display the main to-do list page."""
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    todos = storage.get_user_todos(username)
    completed = storage.get_user_completed(username)
    stats = storage.get_user_stats(username)

    return render_template(
        "index.html", username=username, todos=todos, completed=completed, stats=stats
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template("login.html")

        if storage.verify_user(username, password):
            session["username"] = username
            flash("Welcome back!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "error")
            return render_template("signup.html")

        if storage.create_user(username, password):
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists. Please choose another.", "error")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Handle user logout."""
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/add", methods=["POST"])
def add_task():
    """Add a new task to the list."""
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    task = request.form.get("task")

    if task:
        storage.add_todo(username, task)
        flash("Task added successfully!", "success")
    else:
        flash("Task cannot be empty!", "error")

    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    """Mark a task as completed."""
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    if storage.complete_task(username, task_id):
        flash("Task marked as completed!", "success")
    else:
        flash("Task not found.", "error")

    return redirect(url_for("index"))


@app.route("/delete/<task_type>/<int:task_id>")
def delete_task(task_type, task_id):
    """Delete a task from the list."""
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    if task_type not in ["todos", "completed"]:
        flash("Invalid task type.", "error")
        return redirect(url_for("index"))

    if storage.delete_task(username, task_id, task_type):
        flash("Task deleted successfully!", "success")
    else:
        flash("Task not found.", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    app.run(host=host, port=port, debug=debug)
