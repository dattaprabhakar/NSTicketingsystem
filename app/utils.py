# app/utils.py
from flask import current_app, render_template, flash, redirect, url_for, request
from flask_mail import Message
from app.extensions import mail
from threading import Thread
import functools
from flask_login import current_user

# --- Email Sending ---
def send_async_email(app, msg):
    with app.app_context():
        try: mail.send(msg); current_app.logger.info(f"Email sent: {msg.subject} to {msg.recipients}");
        except Exception as e: current_app.logger.error(f"Email fail: {msg.subject} to {msg.recipients}: {e}")

def send_email(subject, recipients, text_body_template, **kwargs):
    app = current_app._get_current_object()
    if isinstance(recipients, str): recipients = [recipients]
    elif not isinstance(recipients, list): current_app.logger.error(f"Bad recipients: {recipients}."); return
    if not app.config.get('MAIL_USERNAME'): current_app.logger.warning("Mail skip: not configured."); return
    sender = app.config.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME'))
    if not sender: current_app.logger.error("Mail sender missing."); return
    msg = Message(subject, sender=sender, recipients=recipients)
    try: msg.body = render_template(text_body_template + '.txt', **kwargs)
    except Exception as e: current_app.logger.error(f"Email template err {text_body_template}: {e}"); return
    Thread(target=send_async_email, args=[app, msg]).startErr view_users: {e}") if log else None;
    return render_template('admin/user_list.html',title='Users',users=users)