# app/__init__.py
import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv # Import load_dotenv

# --- IMPORTANT: Load .env variables VERY EARLY ---
# Calculate the path to the .env file in the project root
# Assumes __init__.py is in 'app/' and .env is in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
# Load the .env file
dotenv_loaded = load_dotenv(dotenv_path=dotenv_path, verbose=True) # Add verbose=True for debug info

# --- Import extensions AFTER load_dotenv (if they rely on env vars) ---
from .extensions import mongo, login_manager, bcrypt, csrf, mail


# --- Debugging Output ---
print(f"DEBUG: dotenv loaded? {dotenv_loaded}") # Check if load_dotenv reported success
print(f"DEBUG: FLASK_ENV from os.environ after load_dotenv: {os.environ.get('FLASK_ENV')}")
print(f"DEBUG: MONGO_URI from os.environ after load_dotenv: {os.environ.get('MONGO_URI')}")
# --- End Debugging Output ---


def create_app(config_object='config.DevelopmentConfig'):
    """Application Factory Pattern"""
    app = Flask(__name__, instance_relative_config=True)

    # --- Load configuration ---

    # Explicitly get FLASK_ENV from environment (set by .env or manually)
    # Default to 'production' if not found
    flask_env = os.environ.get('FLASK_ENV', 'production')
    app.config['ENV'] = flask_env
    # Set DEBUG based on ENV
    app.config['DEBUG'] = flask_env == 'development'

    # --- Debugging ---
    print(f"DEBUG: app.config['ENV'] set to: {app.config.get('ENV')}")
    print(f"DEBUG: app.config['DEBUG'] set to: {app.config.get('DEBUG')}")
    # --- End Debugging ---


    # Load other configurations from os.environ (which should have .env vars now)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-please-change') # Add a default
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', ('Default Sender', 'noreply@example.com')) # Default tuple
    # (Add your logic here to parse MAIL_DEFAULT_SENDER if it's a string tuple in .env)


    # --- Configure Logging ---
    # This check should now work because app.config['ENV'] was explicitly set above
    print(f"DEBUG: Checking app.config['ENV'] for logging setup: {app.config.get('ENV')}") # Debug before the check
    if app.config['ENV'] == 'development':
        logging.basicConfig(level=logging.INFO)
        print("DEBUG: Logging level set to INFO")
    else:
        logging.basicConfig(level=logging.WARNING)
        print("DEBUG: Logging level set to WARNING")

    app.logger.info("Flask App Configuration Loaded:")
    app.logger.info(f"SECRET_KEY: {'Set' if app.config.get('SECRET_KEY') != 'default-secret-key-please-change' else 'Using Default (Not Set in Env)'}")
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

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.tickets import tickets_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        return render_template('errors/500.html'), 500

    app.logger.info("Help Desk App Initialized")
    return app