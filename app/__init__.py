# app/__init__.py
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from .extensions import mongo, login_manager, bcrypt, csrf, mail
import logging

# Load environment variables from .env file
load_dotenv()

def create_app(config_object='config.DevelopmentConfig'): # Default config class name
    """Application Factory Pattern"""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    # Option 1: Load from .env using os.environ.get
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587)) # Default port
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    # Ensure MAIL_DEFAULT_SENDER is parsed correctly if it's a tuple string in .env
    # Example: MAIL_DEFAULT_SENDER="('Help Desk', 'help@example.com')"
    # You might need eval() for this, but be CAREFUL with eval. Better to set separately.
    # Or define MAIL_SENDER_NAME and MAIL_SENDER_EMAIL in .env
    default_sender_tuple = ('Help Desk App', app.config['MAIL_USERNAME']) # Safer default
    try:
        # Attempt to parse if it looks like a tuple string (use carefully!)
        sender_config = os.environ.get('MAIL_DEFAULT_SENDER')
        if sender_config and sender_config.startswith('(') and sender_config.endswith(')'):
             import ast
             parsed_sender = ast.literal_eval(sender_config)
             if isinstance(parsed_sender, tuple) and len(parsed_sender) == 2:
                 default_sender_tuple = parsed_sender
        app.config['MAIL_DEFAULT_SENDER'] = default_sender_tuple
    except Exception:
        app.config['MAIL_DEFAULT_SENDER'] = default_sender_tuple # Fallback

    # Option 2: Load from instance/config.py (less common with .env)
    # app.config.from_pyfile('config.py', silent=True) # Loads from instance/config.py

    # Option 3: Load directly from a config class (if you define them)
    # app.config.from_object(config_object)

    # Configure Logging
    if app.config['ENV'] == 'development':
        logging.basicConfig(level=logging.INFO) # Log info in dev
    else:
         logging.basicConfig(level=logging.WARNING) # Log warnings/errors in prod

    app.logger.info("Flask App Configuration Loaded:")
    app.logger.info(f"SECRET_KEY: {'Set' if app.config.get('SECRET_KEY') else 'Not Set'}")
    app.logger.info(f"MONGO_URI: {app.config.get('MONGO_URI')}")
    app.logger.info(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")


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

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Log the error here
        app.logger.error(f"Server Error: {error}", exc_info=True)
        # You might want to rollback db session if using SQL
        return render_template('errors/500.html'), 500

    app.logger.info("Help Desk App Initialized")
    return app