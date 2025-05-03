# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
# *** Make sure models and the role decorator are imported correctly ***
from app.models import get_all_users
# Assuming tickets.py is in the same 'routes' directory
try:
    from .tickets import role_required # Relative import for sibling module
except ImportError:
    # Fallback if structure is different or for direct execution (less common)
    from app.routes.tickets import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin') # <--- Make sure this line exists

@admin_bp.route('/')
@login_required
@role_required('agent')
def index():
    return redirect(url_for('admin.view_users'))

@admin_bp.route('/users')
@login_required
@role_required('agent')
def view_users():
    """Displays a list of all registered users."""
    logger = getattr(current_app, 'logger', None) # Get logger safely
    try:
        users = get_all_users()
    except Exception as e:
        flash("An error occurred while fetching users.", "danger")
        if logger: logger.error(f"Error in view_users route: {e}")
        else: print(f"Error in view_users route: {e}")
        users = []

    return render_template('admin/user_list.html', title='User Management', users=users)

# Add more admin routes here later