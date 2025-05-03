# app/models.py
from app.extensions import mongo, login_manager, bcrypt
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from flask import current_app

class User(UserMixin): # Start of the class definition
    # --- Methods INSIDE the class ---
    # MUST BE INDENTED
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role', 'user')

    @staticmethod
    def get(user_id): # <<< THIS METHOD (and others below) MUST BE INDENTED
        """Required by Flask-Login: Load user by ID."""
        logger = getattr(current_app, 'logger', None)
        try:
            if not ObjectId.is_valid(user_id):
                 return None
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                 return User(user_data)
        except Exception as e:
            if logger: logger.error(f"Error User.get {user_id}: {e}")
            # Avoid printing sensitive info in production logs if possible
            # else: print(f"Error User.get {user_id}: {e}")
        return None # Return None if user not found or on error

    @staticmethod
    def find_by_username(username): # INDENTED
        return mongo.db.users.find_one({'username': username})

    @staticmethod
    def find_by_email(email): # INDENTED
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def create(username, email, password, role='user'): # INDENTED
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = mongo.db.users.insert_one({
            'username': username, 'email': email, 'password_hash': hashed_pw,
            'role': role, 'created_at': datetime.utcnow()
        }).inserted_id
        return str(user_id)

    def check_password(self, password): # INDENTED
        # Ensure password_hash exists before checking
        if not self.password_hash:
             return False
        return bcrypt.check_password_hash(self.password_hash, password)
    # --- End of methods inside the class ---

# --- Functions OUTSIDE the class ---
@login_manager.user_loader # Correctly placed decorator outside class
def load_user(user_id):
    return User.get(user_id) # Calls the static method correctly

# --- Ticket Helpers --- (These are standalone functions)
def get_ticket_by_id(ticket_id):
    # ... (implementation) ...
    try: return mongo.db.tickets.find_one({'_id':ObjectId(ticket_id)}); except: return None

def get_user_tickets(user_id):
    # ... (implementation) ...
    return list(mongo.db.tickets.find({'created_by':ObjectId(user_id)}).sort('created_at',-1)) if ObjectId.is_valid(user_id) else []

def get_all_tickets():
    # ... (implementation) ...
     return list(mongo.db.tickets.find().sort('created_at',-1))

# --- Admin Helpers --- (Standalone functions)
def get_all_users():
    # ... (implementation) ...
    log=getattr(current_app,'logger',None); try: return list(mongo.db.users.find({},{'password_hash':0}).sort('username',1)); except Exception as e: log.error(f"Err get_all_users: {e}") if log else None; return []


# --- Role-Based Dashboard Stat Functions --- (Standalone functions)
_ALL_STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened']

def _get_base_ticket_stats():
    # ... (implementation) ...
    stats, logger = {}, getattr(current_app, 'logger', None)
    try:
        stats['total_tickets'] = mongo.db.tickets.count_documents({})
        stats['by_status'] = {s: mongo.db.tickets.count_documents({'status': s}) for s in _ALL_STATUSES}
        stats['high_priority'] = mongo.db.tickets.count_documents({'priority': {'$in': ['High', 'Critical']}})
    except Exception as e:
        if logger: logger.error(f"Error getting base ticket stats: {e}")
        stats = {'total_tickets': 0, 'by_status': {}, 'high_priority': 0}
    for s in _ALL_STATUSES: stats['by_status'].setdefault(s, 0)
    return stats

def get_user_dashboard_stats(user_id):
    # ... (implementation) ...
    stats, logger = {}, getattr(current_app, 'logger', None)
    if not ObjectId.is_valid(user_id): return {'my_total': 0, 'my_open': 0}
    uid_obj = ObjectId(user_id)
    try:
        stats['my_total'] = mongo.db.tickets.count_documents({'created_by': uid_obj})
        stats['my_open'] = mongo.db.tickets.count_documents({'created_by': uid_obj, 'status': 'Open'})
    except Exception as e:
        if logger: logger.error(f"Error get_user_stats {user_id}: {e}")
        stats = {'my_total': 0, 'my_open': 0}
    return stats

def get_admin_dashboard_stats(): return _get_base_ticket_stats()

def get_super_admin_dashboard_stats():
    # ... (implementation) ...
    stats, logger = _get_base_ticket_stats(), getattr(current_app, 'logger', None)
    try:
        stats['total_users'] = mongo.db.users.count_documents({})
        stats['admin_count'] = mongo.db.users.count_documents({'role': {'$in': ['admin', 'super_admin']}})
    except Exception as e:
        if logger: logger.error(f"Error get_super_admin_stats: {e}")
        stats['total_users'], stats['admin_count'] = 'N/A', 'N/A'
    return stats

# Alias (optional)
get_ticket_stats = get_admin_dashboard_stats