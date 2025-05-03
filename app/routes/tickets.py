# app/routes/tickets.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.forms import TicketForm, CommentForm, UpdateStatusForm
from app.models import get_ticket_by_id, get_user_tickets, get_all_tickets, User
from app.extensions import mongo
from app.utils import send_email, roles_required # Use decorator from utils
from bson import ObjectId
from datetime import datetime
import functools

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@tickets_bp.route('/')
@login_required
def list_tickets():
    tickets, logger = [], getattr(current_app, 'logger', None)
    try:
        # Admin/Super Admin see all, user sees their own
        if current_user.role in ['admin', 'super_admin']:
            tickets = get_all_tickets()
        else:
            tickets = get_user_tickets(current_user.id)
        # Populate usernames
        for t in tickets:
            cid = t.get('created_by')
            c_u = User.get(str(cid)) if cid and ObjectId.is_valid(str(cid)) else None
            t['creator_username'] = c_u.username if c_u else '?'
            aid = t.get('assigned_to')
            a_u = User.get(str(aid)) if aid and ObjectId.is_valid(str(aid)) else None
            t['assignee_username'] = a_u.username if a_u else 'N/A'
    except Exception as e:
        flash("Error fetching tickets.", "danger")
        if logger: logger.error(f"List tickets error: {e}")
    return render_template('tickets/ticket_list.html', title='Tickets', tickets=tickets)

@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form, logger = TicketForm(), getattr(current_app, 'logger', None)
    if form.validate_on_submit():
        ticket_data = {
            'title': form.title.data, 'description': form.description.data,
            'priority': form.priority.data, 'status': 'Open',
            'created_by': ObjectId(current_user.id), 'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(), 'assigned_to': None, 'comments': []
        }
        try:
            res = mongo.db.tickets.insert_one(ticket_data)
            flash('Ticket created!', 'success')
            tid = str(res.inserted_id)
            # Email User
            send_email(f"Ticket #{tid}: {form.title.data}", [current_user.email],
                       'email/new_ticket_user', ticket_id=tid, title=form.title.data,
                       username=current_user.username)
            # Email Admins/Super Admins
            agents = [a['email'] for a in mongo.db.users.find({'role': {'$in': ['admin', 'super_admin']}}) if a.get('email')]
            if agents:
                send_email(f"New Ticket #{tid}", agents, 'email/new_ticket_agent',
                           ticket_id=tid, title=form.title.data, creator=current_user.username)
            return redirect(url_for('tickets.list_tickets'))
        except Exception as e:
            flash(f'Error creating ticket: {e}', 'danger')
            if logger: logger.error(f"Create ticket error: {e}")
    return render_template('tickets/create_ticket.html', title='New Ticket', form=form)

@tickets_bp.route('/<ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    logger = getattr(current_app, 'logger', None)
    if not ObjectId.is_valid(ticket_id): abort(404)
    ticket = get_ticket_by_id(ticket_id)
    if not ticket: abort(404)

    # Allow admin/super_admin or ticket creator to view
    if current_user.role not in ['admin', 'super_admin'] and str(ticket.get('created_by')) != current_user.id:
        flash('Permission denied.', 'warning')
        return redirect(url_for('tickets.list_tickets'))

    # Populate details
    creator_user = User.get(str(ticket.get('created_by')))
    ticket['creator_username'] = creator_user.username if creator_user else '?'
    assignee_user = User.get(str(ticket.get('assigned_to')))
    ticket['assignee_username'] = assignee_user.username if assignee_user else 'N/A'
    if 'comments' in ticket:
        for c in ticket['comments']:
            author_user = User.get(str(c.get('author_id')))
            c['author_username'] = author_user.username if author_user else '?'

    comment_form = CommentForm()
    status_form = UpdateStatusForm(data={'status': ticket.get('status', 'Open')})

    if request.method == 'POST':
        # Check comment submission
        if 'submit_comment' in request.form and comment_form.validate_on_submit():
             # Allow admin/super_admin or creator to comment
            if current_user.role in ['admin', 'super_admin'] or str(ticket.get('created_by')) == current_user.id:
                comment = {'_id': ObjectId(), 'author_id': ObjectId(current_user.id), 'text': comment_form.text.data, 'timestamp': datetime.utcnow()}
                try:
                    mongo.db.tickets.update_one({'_id': ObjectId(ticket_id)}, {'$push': {'comments': comment}, '$set': {'updated_at': datetime.utcnow()}})
                    flash('Comment added.', 'success')
                except Exception as e:
                    flash("Error adding comment.", "danger")
                    if logger: logger.error(f"Comment Error T{ticket_id}: {e}")
                return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id)) # Redirect after POST
            else:
                 flash("Permission denied to comment.", "warning")

        # Check status update submission
        elif 'submit_status' in request.form and status_form.validate_on_submit():
            # Allow only admin/super_admin to update status
            if current_user.role in ['admin', 'super_admin']:
                new_status = status_form.status.data
                if new_status != ticket.get('status'):
                    try:
                        mongo.db.tickets.update_one({'_id': ObjectId(ticket_id)}, {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}})
                        flash(f'Status updated to {new_status}.', 'success')
                    except Exception as e:
                        flash("Error updating status.", "danger")
                        if logger: logger.error(f"Status Error T{ticket_id}: {e}")
                else:
                    flash('Status unchanged.', 'info')
                return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id)) # Redirect after POST
            else:
                 flash("Permission denied to update status.", "warning")

        # Handle validation failures if forms were submitted but invalid
        elif 'submit_comment' in request.form:
            flash('Error in comment form.', 'danger')
        elif 'submit_status' in request.form:
            flash('Error updating status.', 'danger')

    # Determine if status form should be shown
    show_status_form = current_user.role in ['admin', 'super_admin']

    return render_template('tickets/ticket_detail.html', title=f"Ticket #{ticket_id}", ticket=ticket, comment_form=comment_form, status_form=status_form, show_status_form=show_status_form)