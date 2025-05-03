# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models import get_all_users
from app.utils import roles_required # <-- Import new decorator

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@roles_required('admin', 'super_admin') # Allow both admin and super_admin
def index, flash # Added flash
from flask_login import login_required,current_user
from app.models import (get_user_dashboard_stats,
                        get_admin_dashboard_stats,
                        get_super_admin_dashboard_stats) # Import specific functions

main_bp=Blueprint('main',__name__)

@main_bp.route('/'); def index(): return redirect(url_for('main.dashboard') if current_user.is_authenticated else url_for('auth.login'))

@main_bp.route('/dashboard'); @login_required
def dashboard():
    role = getattr(current_user, 'role', 'user') # Default to user
    stats = {}
    template_name = 'dashboard_user.html' # Default template

    if role == 'super():
    # Redirect to user list for now
    # A real admin index might show different things based on role later
    return redirect(url_for('admin.view_users'))

@admin_bp.route('/users_admin':
        stats = get_super_admin_dashboard_stats()
        template_name = 'admin/dashboard_super_admin.html'
    elif role == 'admin':
        stats = get_admin_dashboard_stats()
        template_name = 'admin/dashboard_admin.html'
    elif role == '')
@login_required
@roles_required('admin', 'super_admin') # Allow both admin and super_admin
def view_users():
    """Displays a list of all registered users."""
    logger =user':
        stats = get_user_dashboard_stats(current_user.id)
        template_name = 'dashboard_user.html'
    else:
        # Handle unexpected role
        flash(f"Unknown user getattr(current_app, 'logger', None)
    try:
        users = get_all_users()
    except Exception as e:
        flash("Error fetching users.", "danger")
        if logger: logger.error(f"Error view_users: {e}")
        users = []
    # Pass current user role to role '{role}'.", "warning")
        template_name = 'dashboard_user.html' # Fallback to user dashboard
        stats = get_user_dashboard_stats(current_user.id) # Or provide empty stats {} template if needed for conditional display later
    # current_role = getattr(current_user, 'role', None)
    

    return render_template(template_name, title='Dashboard', stats=stats)