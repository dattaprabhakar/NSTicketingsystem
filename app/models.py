# app/models.py
from app.extensions import mongo, login_manager, bcrypt
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash # Older Werkzeug
# If using newer Werkzeug/Flask-Bcrypt, bcrypt handles hashing/checking
from flask_login import UserMixin
from datetime import datetime

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
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
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
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to load a user from the session."""
    return User.get(user_id)

# --- Ticket Model Helpers ---
# (We'll interact directly with mongo.db.tickets in routes for simplicity here,
# but you could create a Ticket class similar to User for more complex logic)

def get_ticket_by_id(ticket_id):
    try:
        return mongo.db.tickets.find_one({'_id': ObjectId(ticket_id)})
    except:
        return None

def get_user_tickets(user_id):
    return list(mongo.db.tickets.find({'created_by': ObjectId(user_id)}).sort('created_at', -1))

def get_all_tickets():
     return list(mongo.db.tickets.find().sort('created_at', -1))

def get_assigned_tickets(agent_id):
    return list(mongo.db.tickets.find({'assigned_to': ObjectId(agent_id)}).sort('created_at', -1))

# --- Dashboard Stats ---
def get_ticket_stats():
    stats = {}
    # Total Tickets
    stats['total_tickets'] = mongo.db.tickets.count_documents({})

    # Tickets by Status
    statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    stats['by_status'] = {}
    for status in statuses:
        stats['by_status'][status] = mongo.db.tickets.count_documents({'status': status})

    # Tickets by Priority (High/Critical only)
    high_priority_count = mongo.db.tickets.count_documents({'priority': {'$in': ['High', 'Critical']}})
    stats['high_priority'] = high_priority_count

    return stats