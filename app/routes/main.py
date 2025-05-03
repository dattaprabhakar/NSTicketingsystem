# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import (get_user_dashboard_stats,
                        get_admin_dashboard_stats,
                        get_super_admin_dashboard_stats)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    role = getattr(current_user, 'role', 'user')
    stats = {}
    template_name = 'dashboard_user.html'

    if role == 'super_admin':
        stats = get_super_admin_dashboard_stats()
        template_name = 'admin/dashboard_super_admin.html'
    elif role == 'admin':
        stats = get_admin_dashboard_stats()
        template_name = 'admin/dashboard_admin.html'
    else: # Default 'user'
        stats = get_user_dashboard_stats(current_user.id)
        template_name = 'dashboard_user.html'

    return render_template(template_name, title='Dashboard', stats=stats)