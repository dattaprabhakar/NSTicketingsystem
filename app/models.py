# app/models.py
from app.extensions import mongo, login_manager, bcrypt
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from flask import current_app

class User(UserMixin):
    # ... (User class methods remain the same) ...
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role', 'user')
    @staticmethod
    def get(user_id):
        logger = getattr(current_app, 'logger', None)
        try:
            if not ObjectId.is_valid(user_id): return None
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data: return User(user_data)
        except Exception as e:
            if logger: logger.error(f"Error User.get {user_id}: {e}")
        return None
    @staticmethod
    def find_by_username(username): return mongo.db.users.find_one({'username': username})
    @staticmethod
    def find_by_email(email): return mongo.db.users.find_one({'email': email})
    @staticmethod
    def create(username, email, password, role='user'):
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = mongo.db.users.insert_one({'username': username, 'email': email, 'password_hash': hashed_pw,'role': role, 'created_at': datetime.utcnow()}).inserted_id
        return str(user_id)
    def check_password(self, password): return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id): return User.get(user_id)

def get_ticket_by_id(ticket_id):
    try: return mongo.db.tickets.find_one({'_id': ObjectId(ticket_id)})
    except: return None
def get_user_tickets(user_id):
    if not ObjectId.is_valid(user_id): return []
    return list(mongo.db.tickets.find({'created_by': ObjectId(user_id)}).sort('created_at', -1))
def get_all_tickets(): return list(mongo.db.tickets.find().sort('created_at', -1))
def get_assigned_tickets(agent_id):
    if not ObjectId.is_valid(agent_id): return []
    return list(mongo.db.tickets.find({'assigned_to': ObjectId(agent_id)}).sort('created_at', -1))
def get_all_users():
    logger = getattr(current_app, 'logger', None)
    try: return list(mongo.db.users.find({}, {'password_hash': 0}).sort('username', 1))
    except Exception as e:
        if logger: logger.error(f"Error get_all_users: {e}")
        return []

# --- Dashboard Stats (UPDATED) ---
def get_ticket_stats():
    stats = {}
    logger = getattr(current_app, 'logger', None)
    # Define all possible statuses, including Reopened
    all_statuses = ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened']
    try:
        stats['total_tickets'] = mongo.db.tickets.count_documents({})
        # Count documents for each status
        stats['by_status'] = {s: mongo.db.tickets.count_documents({'status': s}) for s in all_statuses}
        stats['high_priority'] = mongo.db.tickets.count_documents({'priority': {'$in': ['High', 'Critical']}})
    except Exception as e:
        if logger: logger.error(f"Error getting ticket stats: {e}")
        # Provide default structure on error
        stats = {'total_tickets': 0, 'by_status': {}, 'high_priority': 0}
        # Ensure all keys exist even on error
        for s in all_statuses: stats['by_status'].setdefault(s, 0)
    # Ensure all keys exist even if count was 0 in the DB query
    for s in all_statuses:
        stats['by_status'].setdefault(s, 0)
    return stats