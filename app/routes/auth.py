# app/routes/auth.py
# Remove the invalid syntax from the end of this import line:
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.extensions import mongo, bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- LOGIN ---
@auth_bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    form=LoginForm();
    if form.validate_on_submit():
        u_data=User.find_by_username(form.username.data); u=User(u_data) if u_data else None;
        if u and u.check_password(form.password.data):
            login_user(u); flash('Login OK!','success'); next_p=request.args.get('next'); return redirect(next_p or url_for('main.dashboard'))
        else: flash('Login Fail. Check credentials.','danger')
    # Pass config for potential use in template (like showing dev links)
    return render_template('auth/login.html',title='Login',form=form,config=current_app.config)

# --- LOGOUT ---
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user(); flash('Logged out.','info'); return redirect(url_for('auth.login'))

# --- REGISTER ---
@auth_bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    form=RegistrationForm();
    if form.validate_on_submit():
        try:
            User.create(form.username.data,form.email.data,form.password.data); # Default role is 'user'
            flash('Account created! Please log in.','success'); return redirect(url_for('auth.login'));
        except Exception as e:
             flash(f'Registration error: {e}','danger'); current_app.logger.error(f"Registration error: {e}")
    return render_template('auth/register.html',title='Register',form=form)

# --- SETUP INITIAL USERS (UPDATED ROLES) ---
@auth_bp.route('/setup_initial_user')
def setup_initial_user():
    # WARNING: REMOVE OR PROTECT IN PRODUCTION
    logger = getattr(current_app, 'logger', None)
    users_to_create = [
        {"username": "superadmin", "email": "super@example.com", "password": "password", "role": "super_admin"},
        {"username": "admin1", "email": "admin1@example.com", "password": "password", "role": "admin"},
        {"username": "user1", "email": "user1@example.com", "password": "password", "role": "user"}
    ]
    c, e_count = 0, 0
    for u in users_to_create:
        if not User.find_by_username(u["username"]):
            try:
                User.create(**u); flash(f'User "{u["username"]}" ({u["role"]}) created.','info'); c += 1
            except Exception as ex:
                flash(f'Err creating {u["username"]}: {ex}','danger');
                if logger: logger.error(f'Err setup {u["username"]}: {ex}')
        else:
            flash(f'User "{u["username"]}" exists.','warning'); e_count += 1
    if c == 0 and e_count > 0: flash('Initial users exist.', 'info')
    return redirect(url_for('auth.login'))