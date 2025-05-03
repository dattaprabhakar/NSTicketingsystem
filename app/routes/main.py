# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
# UPD,title=form.title.data,username=current_user.username); agents=[a['email'] for a in mongo.db.users.find({'role':{'$in': ['admin', 'super_admin']}}) if a.get('email')]; send_email(f"New Ticket #{tid}",agents,'email/new_ticket_agent',ticket_id=tid,title=form.title.data,creator=current_user.username) ifATED imports for specific stats
from app.models import (get_user_dashboard_stats,
                        get_admin_dashboard_stats,
                        get_super_admin_dashboard_stats)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth. agents else None; return redirect(url_for('tickets.list_tickets'))
        except Exception as e: flash(f'Err create ticket: {e}','danger'); log.error(f"Create tix err: {e}") if log else None
    return render_template('tickets/create_ticket.html',title='New Ticket',form=form)

@tickets_bp.route('/<ticket_id>',methods=['GET','POST']); @login_required; def view_ticket(ticket_id):
    log=getattr(current_app,'logger',None)
    login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the correct dashboard based on user role."""
    role = getattr(current_user, 'role', 'user') # Default to 'user'

    if role == 'super_admin':
        stats = get_super_admin_dashboard_stats()
        # Pass stats appropriate for super admin template
        return render_template('admin/dashboard_super_admin.html', title='Super Admin Dashboard', stats=stats)

    elif role == 'admin': # Changed from 'agent'
        stats = get_admin_dashboard_stats()
        return render_template('admin/dashboard_if not ObjectId.is_valid(ticket_id): abort(404)
    t=get_ticket_by_id(ticket_id);
    if not t: abort(404)
    # Allow admin and super_admin to view any ticket
    if current_user.role not in ['admin', 'super_admin'] and str(t['created_by'])!=current_user.id: flash('Denied.','warning'); return redirect(url_for('tickets.list_tickets'))
    c_u=User.get(str(tadmin.html', title='Admin Dashboard', stats=stats)

    else: # Default to 'user'
        stats = get_user_dashboard_stats(current_user.id)
        return render_template('dashboard_user.html', title='My Dashboard', stats=stats)