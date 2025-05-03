# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm # Import RegistrationForm if you uncomment the route
from app.models import User
from app.extensions import mongo, bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user_data = User.find_by_username(form.username.data)
        if user_data:
            user = User(user_data) # Create User instance
            if user.check_password(form.password.data):
                login_user(user) # Remember parameter can be added here
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# --- Optional: Add Registration Route ---
# from app.forms import RegistrationForm
# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.dashboard'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         try:
#             # Default role is 'user', can change if needed
#             User.create(form.username.data, form.email.data, form.password.data, role='user')
#             flash('Your account has been created! You are now able to log in', 'success')
#             # Log the user in automatically after registration or redirect to login
#             return redirect(url_for('auth.login'))
#         except Exception as e:
#             flash(f'An error occurred during registration: {e}', 'danger')
#             # Log the error properly in a real app
#     return render_template('auth/register.html', title='Register', form=form)

# --- Create a default admin/agent user (run once manually or via a CLI command) ---
@auth_bp.route('/setup_initial_user')
def setup_initial_user():
    # WARNING: In a real app, protect this route or use a CLI command!
    #          This is just for easy setup during development. REMOVE OR SECURE LATER.
    users_to_create = [
        {"username": "agent1", "email": "agent1@example.com", "password": "password", "role": "agent"},
        {"username": "user1", "email": "user1@example.com", "password": "password", "role": "user"}
    ]
    created_count = 0
    existing_count = 0

    for user_details in users_to_create:
        if not User.find_by_username(user_details["username"]):
            try:
                User.create(user_details["username"], user_details["email"], user_details["password"], user_details["role"])
                flash(f'Initial user "{user_details["username"]}" ({user_details["role"]}) created.', 'info')
                created_count += 1
            except Exception as e:
                 flash(f'Error creating initial user {user_details["username"]}: {e}', 'danger')
        else:
            flash(f'User "{user_details["username"]}" already exists.', 'warning')
            existing_count += 1

    if created_count == 0 and existing_count > 0:
         flash('All initial users already exist.', 'info')
    elif created_count == 0 and existing_count == 0:
         flash('No initial users were specified or an error occurred.', 'warning')


    return redirect(url_for('auth.login'))