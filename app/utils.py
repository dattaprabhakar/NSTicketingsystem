# app/utils.py
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail
from threading import Thread # For sending email asynchronously

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            current_app.logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {msg.recipients}: {e}")


def send_email(subject, recipients, text_body_template, html_body_template=None, **kwargs):
    """Sends an email."""
    app = current_app._get_current_object() # Get the actual app instance
    sender = app.config['MAIL_DEFAULT_SENDER']
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = render_template(text_body_template + '.txt', **kwargs)
    if html_body_template:
         # msg.html = render_template(html_body_template + '.html', **kwargs) # Optional HTML emails
         pass # Keep it simple with text for now

    # Send email in a background thread
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    current_app.logger.info(f"Dispatching email sending thread for subject: {subject}")

# Example Usage within routes:
# from app.utils import send_email
# send_email("Welcome!", [user.email], 'email/welcome')