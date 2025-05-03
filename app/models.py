# app/models.py
from app.extensions import mongo, login_manager, bcrypt; from bson import ObjectId; from werkzeug.security import generate_password_hash, check_password_hash; from flask_login import UserMixin; from datetime import datetime; from flask import current_app
class User(UserMixin):
    def __init__(self,d): self.id=str(d.get('_id')); self.username=d.get('username'); self.email=d.get('email'); self.password_hash=d.get('password_hash'); self.role=d.get('role','user')
    @staticmethod
    def get(uid): log=getattr(current_app,'logger',None); try: return User(mongo.db.users.find_one({'_id':ObjectId(uid)})) if ObjectId.is_valid(uid) and mongo.db.users.find_one({'_id':ObjectId(uid)}) else None; except Exception as e: log.error(f"Err User.get {uid}: {e}") if log else None; return None
    @staticmethod
    def find_by_username(uname): return mongo.db.users.find_one({'username':uname})
    @staticmethod
    def find_by_email(em): return mongo.db.users.find_one({'email':em.is_valid(uid) and mongo.db.users.find_one({'_id':ObjectId(uid)}) else None; except Exception as e: log.error(f"Err User.get {uid}: {e}") if log else print(f"Err User.get {uid}: {e}"); return None
    @staticmethod
    def find_by_username(uname): return mongo.db.users.find_one({'username':uname})
    @staticmethod
    def find_by_email(em): return mongo.db.users.find_one({'email':em})
    @staticmethod
    def create(username,email,password,role='user'): hashed=bcrypt.generate_password_hash(password).decode('utf-8'); uid=mongo.db.users.insert_one({'username':username,'email':email,'password_hash':hashed,'role':role,'created_at':datetime.utcnow()}).inserted_id; return str(uid)
    def check_password(self,pwd): return bcrypt.check_password_hash(self.password_hash,pwd)
@login_manager.user_loader
def load_user(uid): return User.get(uid)

# --- Ticket Helpers ---
def get_ticket_by_id(tid): try: return mongo.db.tickets.find_one({'_id':ObjectId(tid)}); except: return None
def get_user_tickets(uid): return list(mongo.db.tickets.find({'created_by':ObjectId(uid)}).sort('created_at',-1)) if ObjectId.is_valid(uid) else []
def get_all_tickets(): return list(mongo.db.tickets.find().sort('created_at',-1))

# --- Admin Helpers ---
def get_all_users(): log=getattr(current_app,'logger',None); try: return list(mongo.db.users.find({},{'password_hash':0}).sort('username',1)); except Exception as e: log.error(f"Err get_all_users: {e}") if log else print(f"Err get_all_users: {e}"); return []

# --- Role-Based Dashboard Stat Functions (NEW/UPDATED) ---
def get_user_dashboard_stats(user_id):
    stats,log={},getattr(current_app,'logger',None)
    if not ObjectId.is_valid(user_id): return {'my_total': 0, 'my_open': 0}
    uid_obj=ObjectId(user_id)
    try: stats['my_total']=mongo.db.tickets.count_documents({'created_by': uid_obj}); stats['my_open']=mongo.db.tickets.count_documents({'created_by':uid_obj,'status':'Open'})
    except Exception as e: log.error(f"Err get_user_stats {user_id}: {e}") if log else None; stats={'my_total':0,'my_open':0}
    return stats

def get_admin_dashboard_stats():
    stats, log = {}, getattr(current_app, 'logger', None)
    all_statuses = ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened']
    try:
        stats['total_tickets']=mongo.db.tickets.count_documents({})
        stats['by_status']={s:mongo.db.tickets.count_documents({'status':s}) for s in all_statuses}
        stats['high_priority']=mongo.db.tickets.count_documents({'priority':{'$in':['High','Critical']}})
    except Exception as e:
        log.error(f"Err get_admin_stats: {e}") if log else None
        stats = {'total_tickets': 0, 'by_status': {}, 'high_priority': 0}
    for s in all_statuses: stats['by_status'].setdefault(s, 0) # Ensure all keys exist
    return stats

def get_super_admin_dashboard_stats():
    stats, log = get_admin_dashboard_stats(), getattr(current_app, 'logger', None) # Start with admin stats
    try:
        stats['total_users'] = mongo.db.users.count_documents({})
        stats['admin_count'] = mongo.db.users.count_documents({'role': {'$in': ['admin', 'super_admin']}})
    except Exception as e:
        log.error(f"Err get_super_admin_stats: {e}") if log else None
})
    @staticmethod
    def create(username,email,password,role='user'): hashed=bcrypt.generate_password_hash(password).decode('utf-8'); uid=mongo.db.users.insert_one({'username':username,'email':email,'password_hash':hashed,'role':role,'created_at':datetime.utcnow()}).inserted_id; return str(uid)
    def check_password(self,pwd): return bcrypt.check_password_hash(self.password_hash,pwd)
@login_manager.user_loader
def load_user(uid): return User.get(uid)
def get_ticket_by_id(tid): try: return mongo.db.tickets.find_one({'_id':ObjectId(tid)}); except: return None
def get_user_tickets(uid): return list(mongo.db.tickets.find({'created_by':ObjectId(uid)}).sort('created_at',-1)) if ObjectId.is_valid(uid) else []
def get_all_tickets(): return list(mongo.db.tickets.find().sort('created_at',-1))
def get_assigned_tickets(aid): return list(mongo.db.tickets.find({'assigned_to':ObjectId(aid)}).sort('created_at',-1)) if ObjectId.is_valid(aid) else []
def get_all_users(): log=getattr(current_app,'logger',None); try: return list(mongo.db.users.find({},{'password_hash':0}).sort('username',1)); except Exception as e: log.error(f"Err get_all_users: {e}") if log else None; return []

# --- UPDATED/NEW Dashboard Stats ---
_ALL_STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened']
def _get_base_ticket_stats():
    stats, logger = {}, getattr(current_app, 'logger', None)
    try:
        stats['total_tickets'] = mongo.db.tickets.count_documents({})
        stats['by_status'] = {s: mongo.db.tickets.count_documents({'status': s}) for s in _ALL_STATUSES}
        stats['high_priority'] = mongo.db.tickets.count_documents({'priority': {'$in': ['High', 'Critical']}})
    except Exception as e:
        if logger: logger.error(f"Error getting base ticket stats: {e}")
        stats = {'total_tickets': 0, 'by_status': {}, 'high_priority': 0}
    # Ensure all status keys exist
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

def get_admin_dashboard_stats(): return _get_base_ticket_stats() # Admin sees base ticket stats

def get_super_admin_dashboard_stats():
    stats, logger = _get_base_ticket_stats(), getattr(current_app, 'logger', None)
    try:
        stats['total_users'] = mongo.db.users.count_documents({})
        stats['admin_count'] = mongo.db.users.count_documents({'role': {'$in': ['admin', 'super_admin']}})
    except Exception as e:
        if logger: logger.error(f"Error get_super_admin_stats: {e}")
        stats['total_users'], stats['admin_count'] = 'N/A', 'N/A'
    return stats

# Keep old name for compatibility if needed elsewhere, points to admin stats now
get_ticket_stats = get_admin_dashboard_stats