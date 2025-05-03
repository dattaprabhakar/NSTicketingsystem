# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models import get_all_users
from app.utils import roles_required # Use decorator from utils

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@roles_required('admin', 'super_admin')
def index():
    return redirect(url_for('admin.view_users'))

@admin_bp.route('/users')
@login_required
@roles_required('admin', 'super_admin')
def view_users():
    logger = getattr(current_app, 'logger', None)
    users = []
    try:
        users = get_all_users()
    except Exception as e:
        flash("Error fetching users.", "danger")
        if logger: logger.error(f"Error view_users: {e}")
    return render_template('admin/user_list.html', title='Users', users=users)