# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import get_ticket_stats

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html') # Or redirect to login

@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = get_ticket_stats()
    # Pass stats needed for the widgets
    return render_template('dashboard.html', title='Dashboard', stats=stats)