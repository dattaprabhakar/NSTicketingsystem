# app/models.py
# ... (keep existing code for User class, ticket functions, etc.) ...
from flask import current_app # Add this import

# ... (User class definition) ...

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to load a user from the session."""
    return User.get(user_id)

# ... (Ticket model helpers) ...

# --- Admin Panel Functions ---
def get_all_users():
    """Fetches all users from the database, excluding password hash."""
    try:
        # Use projection to exclude the password_hash field
        users_cursor = mongo.db.users.find({}, {'password_hash': 0}).sort('username', 1)
        return list(users_cursor)
    except Exception as e:
        current_app.logger.error(f"Error fetching all users: {e}")
        return [] # Return empty list on error

# ... (get_ticket_stats function) ...