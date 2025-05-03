# app/__init__.py
import os
import logging
import ast
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import datetime # Make sure datetime is imported if used in context_processor

# --- Load .env variables VERY EARLY ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Import extensions AFTER load_dotenv ---
from .extensions import mongo, login_manager, bcrypt, csrf, mail

# --- Import Blueprints ---
# It's often cleaner to import blueprints *inside* create_app
# but importing here is also fine if they don't cause circular dependencies yet.
# Let's keep imports inside create_app for better structure with the factory pattern.


def create_app(config_object='config.DevelopmentConfig'):
    """Application Factory Pattern"""
    app = Flask(__name__, instance_relative_config=True) # <<< 'app' is created HERE

    # --- Load configuration ---
    # ... (config loading code remains the same) ...
    flask_env = os.environ.get('FLASK_ENV', 'production').lower()
    app.config['ENV'] = flask_env
    app.config['DEBUG'] = flask_env == 'development'
    app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False').lower() == 'true'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-please-change')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    # ... (Mail config loading) ...
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    # ... (Mail default sender parsing) ...
    default_sender_config = os.environ.get('MAIL_DEFAULT_SENDER')
    default_sender_tuple = ('Help Desk App', app.config.get('MAIL_USERNAME', '')) # Default
    if default_sender_config:
        try:
            if default_sender_config.strip().startswith('(') and default_sender_config.strip().endswith(')'):
                 parsed_sender = ast.literal_eval(default_sender_config)
                 if isinstance(parsed_sender, tuple) and len(parsed_sender) == 2: default_sender_tuple = parsed_sender
                 else: app.logger.warning("MAIL_DEFAULT_SENDER in .env is not a valid 2-element tuple string. Using default.")
            else: default_sender_tuple = ('Help Desk App', default_sender_config)
        except (ValueError, SyntaxError, TypeError) as e: app.logger.warning(f"Could not parse MAIL_DEFAULT_SENDER '{default_sender_config}': {e}. Using default.")
    app.config['MAIL_DEFAULT_SENDER'] = default_sender_tuple


    # --- Configure Logging ---
    log_level = logging.INFO if app.config['ENV'] == 'development' else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
    # ... (logging info messages) ...
    app.logger.info("Flask App Configuration Loaded:")
    # ...


    # --- Initialize extensions --- (Needs the 'app' object)
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Add now() to Jinja globals for use in templates (e.g., footer year)
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    # --- Register Blueprints --- (Needs the 'app' object)
    # *** MOVED INSIDE create_app ***
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.tickets import tickets_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    # *** END OF MOVE ***

    # --- Error Handlers --- (Needs the 'app' object)
    @app.errorhandler(404)
    def not_found_error(error):
        # Import request here if needed, or rely on global context
        from flask import request
        app.logger.debug(f"Handling 404 error for path: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        return render_template('errors/500.html'), 500

    app.logger.info("Help Desk App Initialized")
    return app  # <<< Return the configured app instance

# --- DO NOT PUT CODE THAT USES 'app' OUTSIDE THE create_app FUNCTION ---
# Error was here: app.register_blueprint(auth_bp) was outside the function