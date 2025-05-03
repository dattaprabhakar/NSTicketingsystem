# app/__init__.py
import os
import logging
import ast
from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Import extensions AFTER load_dotenv
from .extensions import mongo, login_manager, bcrypt, csrf, mail

def create_app():
    """Application Factory Pattern"""
    app = Flask(__name__, instance_relative_config=True)

    # --- Load Configuration ---
    flask_env = os.environ.get('FLASK_ENV', 'production').lower()
    app.config.update(
        ENV=flask_env,
        DEBUG=flask_env == 'development',
        TESTING=os.environ.get('FLASK_TESTING', 'False').lower() == 'true',
        SECRET_KEY=os.environ.get('SECRET_KEY', 'default-secret-key-please-change'),
        MONGO_URI=os.environ.get('MONGO_URI'),
        MAIL_SERVER=os.environ.get('MAIL_SERVER'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true',
        MAIL_USE_SSL=os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true',
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    )
    # Parse MAIL_DEFAULT_SENDER
    sender_config = os.environ.get('MAIL_DEFAULT_SENDER')
    sender_tuple = ('Help Desk App', app.config.get('MAIL_USERNAME', ''))
    if sender_config:
        try:
            # Check if it looks like a tuple string '("Name", "email")'
            if sender_config.strip().startswith('(') and sender_config.strip().endswith(')'):
                parsed = ast.literal_eval(sender_config)
                if isinstance(parsed, tuple) and len(parsed) == 2:
                    sender_tuple = parsed
                else: # Malformed tuple string
                     app.logger.warning("MAIL_DEFAULT_SENDER format error (not 2-tuple). Using default.")
            else: # Assume it's just the email address
                sender_tuple = ('Help Desk', sender_config)
        except Exception as e:
            app.logger.warning(f"Could not parse MAIL_DEFAULT_SENDER: {e}. Using default.")
    app.config['MAIL_DEFAULT_SENDER'] = sender_tuple

    # --- Configure Logging ---
    log_level = logging.INFO if app.config['DEBUG'] else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

    # --- Initialize Extensions ---
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # --- Context Processors ---
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    # --- Register Blueprints ---
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.tickets import tickets_bp
    from .routes.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.debug(f"404 error for path: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Server Error: {error}", exc_info=True)
        return render_template('errors/500.html'), 500

    app.logger.info(f"Help Desk App Initialized (Env: {app.config['ENV']})")
    return app