# app/models.py
# *** Import extensions first ***
from app.extensions import mongo, login_manager, bcrypt
# *** Other imports ***
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash # Older Werkzeug
from flask_login import UserMixin
from datetime import datetime
from flask import current_app # Import current_app if needed for logging

# --- User Model ---
class User(UserMixin):
    """Custom User class for Flask-Login."""
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role', 'user') # Default role is 'user'

    @staticmethod
    def get(user_id):
        """Required by Flask-Login: Load user by ID."""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except Exception as e:
            # Use logger if available, otherwise print
            logger = getattr(current_app, 'logger', None)
            if logger:
                logger.error(f"Error in User.get for user_id {user_id}: {e}")
            else:
                print(f"Error in User.get for user_id {user_id}: {e}")
            return None
        return None

    @staticmethod
    def find_by_username(username):
        """Find user by username."""
        return mongo.db.users.find_one({'username': username})

    @staticmethod
    def find_by_email(email):
        """Find user by email."""
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def create(username, email, password, role='user'):
        """Create a new user."""
        # Use bcrypt directly from the imported extension
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password_hash': hashed_pw,
            'role': role,
            'created_at': datetime.utcnow()
        }).inserted_id
        return str(user_id)

    def check_password(self, password):
        """Check provided password against the stored hash."""
         # Use bcrypt directly from the imported extension
        return bcrypt.check_password_hash(self.password_hash, password)

# *** Decorator now comes AFTER the import ***
@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to load a user from the session."""
    return User.get(user_id)

# --- Ticket Model Helpers ---
# (Keep the existing ticket helper functions: get_ticket_by_id, get_user_tickets, etc.)
def get_ticket_by_id(ticket_id):
    try:
        return mongo.db.tickets.find_one({'_id': ObjectId(ticket_id)})
    except:
        return None

def get_user_tickets(user_id):
    if not ObjectId.is_valid(user_id): return []
    return list(mongo.db.tickets.find({'created_by': ObjectId(user_id)}).sort('created_at', -1))

def get_all_tickets():
     return list(mongo.db.tickets.find().sort('created_at', -1))

def get_assigned_tickets(agent_id):
    if not ObjectId.is_valid(agent_id): return []
    return list(mongo.db.tickets.find({'assigned_to': ObjectId(agent_id)}).sort('created_at', -1))


# --- Admin Panel Functions ---
def get_all_users():
    """Fetches all users from the database, excluding password hash."""
    try:
        users_cursor = mongo.db.users.find({}, {'password_hash': 0}).sort('username', 1)
        return list(users_cursor)
    except Exception as e:
        # Use logger if available
        logger = getattr(current_app, 'logger', None)
        if logger:
            logger.error(f"Error fetching all users: {e}")
        else:
            print(f"Error fetching all users: {e}")
        return []

# --- Dashboard Stats ---
# (Keep the existing get_ticket_stats function)
def get_ticket_stats():
    stats = {}
    try:
        stats['total_tickets'] = mongo.db.tickets.count_documents({})
        statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
        stats['by_status'] = {s: mongo.db.tickets.count_documents({'status': s}) for s in statuses}
        stats['high_priority'] = mongo.db.tickets.count_documents({'priority': {'$in': ['High', 'Critical']}})
    except Exception as e:
        logger = getattr(current_app, 'logger', None)
        if logger:
            logger.error(f"Error getting ticket stats: {e}")
        else:
            print(f"Error getting ticket stats: {e}")
        stats = {'total_tickets': 0, 'by_status': {}, 'high_priority': 0}
    return stats