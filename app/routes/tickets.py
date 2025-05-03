# app/routes/tickets.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.forms import TicketForm, CommentForm, UpdateStatusForm
from app.models import get_ticket_by_id, get_user_tickets, get_all_tickets, User
from app.extensions import mongo
from app.utils import send_email
from bson import ObjectId
from datetime import datetime
import functools # For role decorator

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

# --- Role Decorator ---
def role_required(role="agent"):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                 flash(f"You do not have permission to access this page. Requires '{role}' role.", "warning")
                 # Redirect to dashboard or appropriate page
                 return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Routes ---

@tickets_bp.route('/')
@login_required
def list_tickets():
    if current_user.role == 'agent':
        # Agents see all tickets for simplicity, could refine to assigned/unassigned
        tickets = get_all_tickets()
    else:
        # Regular users only see their own tickets
        tickets = get_user_tickets(current_user.id)

    # Add user details to tickets for display
    for ticket in tickets:
        creator = User.get(str(ticket.get('created_by')))
        ticket['creator_username'] = creator.username if creator else 'Unknown'
        if ticket.get('assigned_to'):
            assignee = User.get(str(ticket.get('assigned_to')))
            ticket['assignee_username'] = assignee.username if assignee else 'Unassigned'
        else:
             ticket['assignee_username'] = 'Unassigned'

    return render_template('tickets/ticket_list.html', title='My Tickets', tickets=tickets)

@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket_data = {
            'title': form.title.data,
            'description': form.description.data,
            'priority': form.priority.data,
            'status': 'Open', # Initial status
            'created_by': ObjectId(current_user.id),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'assigned_to': None, # Initially unassigned
            'comments': []
        }
        try:
            result = mongo.db.tickets.insert_one(ticket_data)
            flash('Ticket created successfully!', 'success')

            # --- Email Notification ---
            # Notify user
            send_email(
                subject=f"Ticket Created: #{result.inserted_id}",
                recipients=[current_user.email],
                text_body_template='email/new_ticket_user',
                ticket_id=result.inserted_id,
                title=form.title.data
            )
            # Notify agents (find agents - basic example, find all agents)
            agents = mongo.db.users.find({'role': 'agent'})
            agent_emails = [agent['email'] for agent in agents if agent.get('email')]
            if agent_emails:
                 send_email(
                    subject=f"New Ticket Submitted: #{result.inserted_id}",
                    recipients=agent_emails,
                    text_body_template='email/new_ticket_agent',
                    ticket_id=result.inserted_id,
                    title=form.title.data,
                    creator=current_user.username
                 )
            # --- End Email ---

            return redirect(url_for('tickets.list_tickets'))
        except Exception as e:
             flash(f'Error creating ticket: {e}', 'danger')
             # Log error properly

    return render_template('tickets/create_ticket.html', title='Create New Ticket', form=form)


@tickets_bp.route('/<ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)

    # Authorization: User can see their own ticket, Agents can see all
    if current_user.role != 'agent' and str(ticket['created_by']) != current_user.id:
         flash('You do not have permission to view this ticket.', 'warning')
         return redirect(url_for('tickets.list_tickets'))

    # Fetch user details for display
    creator = User.get(str(ticket.get('created_by')))
    ticket['creator_username'] = creator.username if creator else 'Unknown'
    if ticket.get('assigned_to'):
        assignee = User.get(str(ticket.get('assigned_to')))
        ticket['assignee_username'] = assignee.username if assignee else 'Unassigned'
    else:
         ticket['assignee_username'] = 'Unassigned'

    # Add usernames to comments
    for comment in ticket.get('comments', []):
         author = User.get(str(comment.get('author_id')))
         comment['author_username'] = author.username if author else 'Unknown'


    comment_form = CommentForm()
    status_form = UpdateStatusForm(data={'status': ticket['status']}) # Pre-fill status

    if comment_form.validate_on_submit() and comment_form.submit.data:
        if current_user.role == 'agent' or str(ticket['created_by']) == current_user.id:
            new_comment = {
                'author_id': ObjectId(current_user.id),
                'text': comment_form.text.data,
                'timestamp': datetime.utcnow()
            }
            mongo.db.tickets.update_one(
                {'_id': ObjectId(ticket_id)},
                {'$push': {'comments': new_comment}, '$set': {'updated_at': datetime.utcnow()}}
            )
            flash('Comment added.', 'success')
            # Add email notification for comment here if needed
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        else:
            flash('You cannot comment on this ticket.', 'warning')

    # Status update handled by a separate route or conditional logic here
    # Let's handle it inline for simplicity (agents only)
    if status_form.validate_on_submit() and status_form.submit.data and current_user.role == 'agent':
        new_status = status_form.status.data
        if new_status != ticket['status']:
            mongo.db.tickets.update_one(
                {'_id': ObjectId(ticket_id)},
                {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
            )
            flash(f'Ticket status updated to {new_status}.', 'success')
             # Add email notification for status change here if needed
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        else:
             flash('Status is already set to the selected value.', 'info')


    return render_template(
        'tickets/ticket_detail.html',
        title=f"Ticket #{ticket_id}",
        ticket=ticket,
        comment_form=comment_form,
        status_form=status_form # Pass status form only if agent?
    )

# --- Optional: Route for Agent to Assign Ticket ---
# @tickets_bp.route('/<ticket_id>/assign', methods=['POST'])
# @login_required
# @role_required('agent') # Use the decorator
# def assign_ticket(ticket_id):
#     # Logic to get agent_id from form/request
#     agent_id_to_assign = request.form.get('agent_id')
#     if agent_id_to_assign:
#        # Validate agent_id exists and is an agent
#        agent = mongo.db.users.find_one({'_id': ObjectId(agent_id_to_assign), 'role': 'agent'})
#        if agent:
#             mongo.db.tickets.update_one(
#                 {'_id': ObjectId(ticket_id)},
#                 {'$set': {'assigned_to': ObjectId(agent_id_to_assign), 'updated_at': datetime.utcnow()}}
#             )
#             flash(f'Ticket assigned to {agent["username"]}.', 'success')
#              # Notify assigned agent
#        else:
#             flash('Invalid agent selected.', 'danger')
#     else:
#         # Logic for self-assignment maybe?
#         mongo.db.tickets.update_one(
#                 {'_id': ObjectId(ticket_id)},
#                 {'$set': {'assigned_to': ObjectId(current_user.id), 'updated_at': datetime.utcnow()}}
#             )
#         flash(f'Ticket assigned to you.', 'success')

#     return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))