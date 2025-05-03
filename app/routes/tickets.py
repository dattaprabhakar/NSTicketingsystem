# app/routes/tickets.get('created_by'))); t['creator_username']=c_u.username if c_u else '?'; a_u=User.get(str(t.get('assigned_to'))); t['assignee_username']=a_u.username if a_u else 'N/A'
    if 'comments' in t:
        for c in t['comments']: auth_u=User.get(str(c.get('author_id'))); c['author_username']=auth_u.username if auth_u else '?'
    c_form,s_form=CommentForm(),UpdateStatusForm(data={'status':t.get('status','.py
from flask import Blueprint,render_template,redirect,url_for,flash,request,abort,current_app; from flask_login import login_required,current_user; from app.forms import TicketForm,CommentForm,UpdateStatusForm; from app.models import get_ticket_by_id,get_user_tickets,get_all_tickets,User; from app.extensions import mongo; from app.utils import send_Open')})
    if request.method=='POST':
        # Allow admin/super_admin or creator to comment
        if 'submit_comment' in request.form and c_form.validate_on_submit() and (current_user.role in ['admin', 'super_admin'] or str(t['created_by'])==current_user.id):
            comm={'_id':ObjectId(),'author_id':ObjectId(current_user.id),'text':c_form.text.data,'timestamp':datetime.utcnow()}
            try: mongo.db.tickets.update_one({'_id':ObjectId(ticket_id)},{'$push':{'comments':commemail, roles_required # <-- Import new decorator if needed here
from bson import ObjectId; from datetime import datetime; import functools

tickets_bp=Blueprint('tickets',__name__,url_prefix='/tickets')

# Optional: Remove the old role_required decorator definition from here if you moved it to utils.py
# def role_required(role="agent"): ... (OLD DECORATOR) ...

# --- Routes ---
# Use @roles_required('admin', 'super_admin') on routes that need it
@tickets_bp.route('/'); @login_required; def list_tickets():
    tix,log=[],getattr(current_app,'logger',None)
    try:},'$set':{'updated_at':datetime.utcnow()}}); flash('Comment OK.','success');
            except Exception as e: flash("Err comment.","danger"); log.error(f"Comment Err T{ticket_id}: {e}") if log else None;
            return redirect(url_for('tickets.view_ticket',ticket_id=ticket_id))
        # Only Admin/Super_Admin can update status
        elif 'submit_status' in request.form and s_form.validate_on_submit() and current_user.role in ['admin
        # Admin/Super Admin see all, user sees their own
        if current_user.role in ['admin', 'super_admin']: tix = get_all_tickets()
        else: tix = get_user_tickets(current_user.id)
        # Populate usernames (simplified)
        for t in tix:
            cid=t.get('created_by'); c_u=User.get(str(cid)) if cid and ObjectId.is_valid(str(cid)) else None; t['creator_username']=c_u.username if c_u else '?'
            aid=t.get('assigned_to'); a_u=User.', 'super_admin']:
            new_s=s_form.status.data
            if new_s!=t.get('status'): try: mongo.db.tickets.update_one({'_id':ObjectId(ticket_id)},{'$set':{'status':new_s,'updated_at':datetime.utcnow()}}); flash(f'Status -> {new_s}.','success'); except Exception as e: flash("Err status.","danger"); log.error(f"Status Err T{ticket_id}: {e}") if log else None;
            else: flash('Status same.','info')
            return redirect(url_for('tickets.view_ticket',ticket_id=ticket_id))
        elif 'submit_comment' in request.form: flash('Bad comment.','dangerget(str(aid)) if aid and ObjectId.is_valid(str(aid)) else None; t['assignee_username']=a_u.username if a_u else 'N/A'
    except Exception as e: flash("Err fetch tickets.","danger"); log.error(f"List tix err: {e}") if log else None
    return render_template('tickets/ticket_list.html',title='Tickets',tickets=tix)

@tickets_bp.route('/new',methods=['GET','POST']); @login_required; def create_ticket():
    form,log=TicketForm(),getattr(current_app,'logger',None)
    if form.validate_on_submit():
        t_data={'title':form.title.data')
        elif 'submit_status' in request.form: flash('Bad status.','danger')
    can_update_status = current_user.role in ['admin', 'super_admin'] # Pass flag to template
    return render_template('tickets/ticket_detail.html',title=f"Ticket #{ticket_id}",ticket=t,comment_form=c_form,status_form=s_form, can_update_status=can_update_status)