# app/__init__.py
import os
import logging
import ast # For parsing tuple from env var if needed
from flask import Flask, render_template
from dotenv import load_dotenv

# --- Load .env variables VERY EARLY ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Import extensions AFTER load_dotenv ---
from .extensions import mongo, login_manager, bcrypt, csrf, mail

def create_app(config_object='config.DevelopmentConfig'): # Default config class name (can be ignored if using env)
    """Application Factory Pattern"""
    app = Flask(__name__, instance_relative_config=True)

    # --- Load configuration ---

    # Explicitly get FLASK_ENV from environment (set by .env or manually)
    # Default to 'production' if not found
    flask_env = os.environ.get('FLASK_ENV', 'production').lower()
    app.config['ENV'] = flask_env
    # Set DEBUG based on ENV
    app.config['DEBUG'] = flask_env == 'development'
    app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False').lower() == 'true'


    # Load other configurations from os.environ (which should have .env vars now)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-please-change')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

    # Mail Configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

    # Parse MAIL_DEFAULT_SENDER from env var string potentially like "('Name', 'email@example.com')"
    default_sender_config = os.environ.get('MAIL_DEFAULT_SENDER')
    default_sender_tuple = ('Help Desk App', app.config.get('MAIL_USERNAME', '')) # Default
    if default_sender_config:
        try:
            # Safely evaluate if it looks like a tuple string
            if default_sender_config.strip().startswith('(') and default_sender_config.strip().endswith(')'):
                 parsed_sender = ast.literal_eval(default_sender_config)
                 if isinstance(parsed_sender, tuple) and len(parsed_sender) == 2:
                     default_sender_tuple = parsed_sender
                 else:
                      app.logger.warning("MAIL_DEFAULT_SENDER in .env is not a valid 2-element tuple string. Using default.")
            else:
                # Assume it's just the email address if not a tuple string
                default_sender_tuple = ('Help Desk App', default_sender_config)
        except (ValueError, SyntaxError, TypeError) as e:
            app.logger.warning(f"Could not parse MAIL_DEFAULT_SENDER '{default_sender_config}': {e}. Using default.")
    app.config['MAIL_DEFAULT_SENDER'] = default_sender_tuple


    # --- Configure Logging ---
    log_level = logging.INFO if app.config['ENV'] == 'development' else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

    app.logger.info("Flask App Configuration Loaded:")
    app.logger.info(f"SECRET_KEY: {'Set' if app.config.get('SECRET_KEY') != 'default-secret-key-please-change' else 'Using Default/Not Set'}")
    app.logger.info(f"MONGO_URI: {app.config.get('MONGO_URI')}")
    app.logger.info(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    app.logger.info(f"Flask App Environment (ENV): {app.config['ENV']}")
    app.logger.info(f"Flask App Debug Mode: {app.config['DEBUG']}")

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Add now() to Jinja globals for use in templates (e.g., footer year)
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.tickets import tickets_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp)

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.debug(f"Handling 404 error for path: {request.path}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True) # Log the full traceback
        # You might want to rollback db session if using SQL
        return render_template('errors/500.html'), 500

    app.logger.info("Help Desk App Initialized")
    return app