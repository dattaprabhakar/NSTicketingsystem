# app/models.py
from app.extensions import mongo, login_manager, bcrypt
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from flask import current_app

class User(UserMixin):
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

    def syntax for defining a function body with complex logic like `try...except`.

**The Solution:**

The `get_all_users` function needs to be written with standard Python indentation for the function body, `try` block, and `except` block.

**Corrected `app/models.py`:**

```python
# app/models.py
from app.extensions import mongo, login_manager, bcrypt
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from flask import current_app

class User(UserMixin):
    # --- Methods INSIDE the class ---
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

    def check_password(self, password):
        if not self.password_hash: return False
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id): return User.get(user_id)

# --- Ticket Helpers ---
def get_ticket_by_id(ticket_id):
    logger = getattr(current_app, 'logger', None)
    try:
        if ObjectId.is_valid(ticket_id):
            return mongo.db.tickets.find_one({'_id': ObjectId(ticket_id)})
        else:
            if logger: logger.warning(f"Invalid ObjectId passed to get_ticket_by_ check_password(self, password):
        if not self.password_hash: return False
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id): return User.get(user_id)

# --- Ticket Helpers ---
def get_ticket_by_id(ticket_id):
    logger = getattr(current_app, 'logger', None)
    try:
        if ObjectId.is_valid(ticket_id):
            return mongo.db.tickets.find_one({'_id': ObjectId(ticket_id)})
        else:
            if logger: logger.warning(f"Invalid ObjectId passed to get_ticket_by_id: {ticket_id}")
            return None
    except Exception as e:
        if logger: logger.error(f"Error fetching ticket {ticket_id}: {e}")
        return None

def get_user_tickets(user_id): return list(mongo.db.tickets.find({'created_by':ObjectId(user_id)}).sort('created_at',-1)) if ObjectId.is_valid(user_id) else []
def get_all_tickets(): return list(mongo.db.tickets.find().sort('created_at',-1))

# --- Admin Helpers ---
# *** CORRECTED SYNTAX for get_all_users ***
def get_all_users():
    """Fetches all users from the database, excluding password hash."""
    logger = getattr(current_app, 'logger', None)
    try:
        users_cursor = mongo.db.users.find({}, {'password_hash': 0}).sort('username', 1)
        return list(users_cursor)
    except Exception as e:
        if logger:
            logger.error(f"Error getting all users: {e}")
        # else: # Optional: print if no logger for local dev debugging
        #     print(f"Error getting all users: {e}")
        return [] # Return empty list on error
# *** END CORRECTION ***


# --- Role-Based Dashboard Stat Functions ---
_ALL_STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened']
def _get_base_ticket_stats():
    stats, logger = {}, getattr(current_app, 'logger', None)
    try:
        stats['total_tickets'] = mongo.db.tickets.count_documents({})
        stats['by_status'] = {s: mongo.db.tickets.count_documents({'status': s}) for s in _ALL_STATUSES}
        stats['high_priority'] = mongo.db.tickets.count_documents({'priority': {'$in': ['High',id: {ticket_id}")
            return None
    except Exception as e:
        if logger: logger.error(f"Error fetching ticket {ticket_id}: {e}")
        return None

def get_user_tickets(user_id): return list(mongo.db.tickets.find({'created_by':ObjectId(user_id)}).sort('created_at',-1)) if ObjectId.is_valid(user_id) else []
def get_all_tickets(): return list(mongo.db.tickets.find().sort('created_at',-1))

# --- Admin Helpers ---
# *** CORRECTED SYNTAX for get_all_users ***
def get_all_users():
    """Fetches all users from the database, excluding password hash."""
    log = getattr(current_app, 'logger', None)
    try:
        # Use projection to exclude password_hash, sort by username
        users_cursor = mongo.db.users.find({}, {'password_hash': 0}).sort('username', 1)
        return list(users_cursor)
    except Exception as e:
        if log:
            log.error(f"Error fetching all users: {e}")
        # else: # Avoid printing in production if possible
        #     print(f"Error fetching all users: {e}")
        return [] # Return empty list on error
# *** END CORRECTION ***

# 'Critical']}})
    except Exception as e:
        if logger: logger.error(f"Error getting base ticket stats: {e}")
        stats = {'total_tickets': 0, 'by_status': {}, 'high_priority': 0}
    for s in _ALL_STATUSES: stats['by_status'].setdefault(s, 0)
    return stats
def get_user_dashboard_stats(user_id):
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
    stats, logger --- Role-Based Dashboard Stat Functions ---
_ALL_STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened']
def _get_base_ticket_stats():
    stats, logger = {}, getattr(current_app, 'logger', None)
    try:
        stats['total_tickets'] = mongo.db.tickets.count_documents({})
        stats['by_status'] = {s: mongo.db.tickets.count_documents({'status': s}) for s in _ALL_STATUSES}
        stats['high_priority'] = mongo.db.tickets.count_documents({'priority': {'$in': ['High', 'Critical']}})
    except Exception as e:
        if logger: logger.error(f"Error getting = _get_base_ticket_stats(), getattr(current_app, 'logger', None)
    try:
        stats['total_users'] = mongo.db.users.count_documents({})
        stats['admin_count'] = mongo.db.users.count_documents({'role': {'$in': ['admin', 'super_admin']}})
    except Exception as e:
        if logger: logger.error(f"Error get_super_admin_stats: {e}")
        stats['total_users'], stats['admin_count'] = 'N/A', 'N/A'
    return stats
get_ticket_stats = get_admin_dashboard_stats # Alias for admin dashboard