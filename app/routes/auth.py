# app/routes/auth.pyuser_tickets,get_all_tickets,User; from app.extensions import mongo; from app.utils import send_email; from bson import ObjectId; from datetime import datetime; import functools
tickets_bp=Blueprint('tickets',__name__,url
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app;_prefix='/tickets')

# --- UPDATED DECORATOR ---
# Now checks against 'admin' role by from flask_login import login_user, logout_user, login_required, current_user; from app. default, but can accept others
# Consider moving this decorator to utils.py or extensions.py if used by multiple blueprintsforms import LoginForm, RegistrationForm; from app.models import User; from app.extensions import mongo, bcrypt
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- LOGIN ---
@auth_
def role_required(role="admin"): # Default check is now 'admin'
    def decorator(fbp.route('/login',methods=['GET','POST']); def login():
    if current_user.is_authenticated: return):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs): redirect(url_for('main.dashboard'))
    form=LoginForm();
    if form.validate_on
            # Ensure user is logged in first
            if not current_user.is_authenticated:
                 flash_submit(): u_data=User.find_by_username(form.username.data); u=User("Please log in.", "info")
                 return redirect(url_for('auth.login', next=request.path))(u_data) if u_data else None;
        if u and u.check_password(form.password.data): login_user(u); flash('Login OK!','success'); next_p=request
            # Check role
            if getattr(current_user, 'role', None) != role:
                 .args.get('next'); return redirect(next_p or url_for('main.dashboard'))
        else: flash('Login Fail. Check credentials.','danger')
    return render_template('auth/login.# Allow super_admin to access admin routes as well
                 if role == "admin" and getattr(current_user, 'role', None) == "super_admin":
                      pass # Allow super_admin access
                 else:html',title='Login',form=form,config=current_app.config)

# --- LOGOUT ---
@
                      flash(f"Permission Denied. Requires '{role}' role.", "warning")
                      return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_functionauth_bp.route('/logout'); @login_required; def logout(): logout_user(); flash('Logged out.','info'); return redirect(url_for('auth.login'))

# --- REGISTER ---
@auth_bp.
    return decorator
# --- END UPDATED DECORATOR ---

@tickets_bp.route('/'); @login_required; def list_tickets():
    # ... (list_tickets code remains the same) ...
    tix,log=[],getattr(current_app,'logger',None)
    try:
        if current_user.role inroute('/register',methods=['GET','POST']); def register():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    form=RegistrationForm();
    if form.validate_on_submit(): try: User.create(form.username.data,form.email.data,form ['admin', 'super_admin']: tix=get_all_tickets() # Admin/Super see all
        else: tix=get_user_tickets(current_user.id)
        for t in tix: cid=t.get('created_by'); c_u=User.get(str(cid)) if cid and ObjectId.password.data); flash('Account created! Please log in.','success'); return redirect(url_for('auth.login')); except Exception as e: flash(f'Reg error: {e}','danger'); current_app.logger.error(f"Reg error: {e}")
    return render_template('auth/register.html',title='Register',form=form)

# --- SETUP INITIAL USERS (UPDATED ROLES) ---
@auth_bp.route('/setup_initial_user'); def setup_initial_user():
    logger = getattr(current_app.is_valid(str(cid)) else None; t['creator_username']=c_u.username if, 'logger', None)
    users_to_create = [
        {"username": "superadmin", "email": "super@example.com", "password": "password", "role": "super_admin"},
        {"username": "admin1", "email": "admin1@example.com", "password": "password", c_u else '?'; aid=t.get('assigned_to'); a_u=User.get(str(aid)) if aid and ObjectId.is_valid(str(aid)) else None; t['assignee_username']=a_u.username if a_u else 'N/A'
    except Exception as e "role": "admin"}, # Was agent1
        {"username": "user1", "email": "user1@example.com", "password": "password", "role": "user"}
    ]
    c, e_count = 0, 0
    for u in users_to_create:
        if not User.find_by_username(u["username"]):
            try: User.create(**u); flash(: flash("Err fetch tickets.","danger"); log.error(f"List tix err: {e}") if log else None
    return render_template('tickets/ticket_list.html',title='Tickets',tickets=tix)

@tickets_bp.route('/new',methods=['GET','POST']); @login_required; def create_ticket():
    # ... (create_ticket code remains the same) ...
    form,log=TicketForm(),getattr(current_app,'logger',None)
    if form.validate_on_submit():
        t_data={'title':form.title.data,'description':form.description.data,'priority':f'User "{u["username"]}" ({u["role"]}) created.','info'); c += 1
            except Exception as ex: flash(f'Err creating {u["username"]}: {ex}','danger'); logger.error(fform.priority.data,'status':'Open','created_by':ObjectId(current_user.id),'created_at':datetime.utcnow(),'updated_at':datetime.utcnow(),'assigned_to':None,'comments':[]}
        try: res=mongo.db.tickets.insert_one(t_data); flash('Ticket created!'Err setup {u["username"]}: {ex}') if logger else None
        else: flash(f'User "{u["username"]}" exists.','warning'); e_count += 1
    if c == 0 and e_count > 0: flash('Initial users exist.', 'info')
    return redirect(url_for('auth.login','success'); tid=str(res.inserted_id); send_email(f"Ticket #{tid}: {form.title.data}",[current_user.email],'email/new_ticket_user',ticket_id=tid'))