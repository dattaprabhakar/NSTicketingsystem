# app/__init__.py
# ... (other imports) ...

def create_app(config_object='config.DevelopmentConfig'):
    # ... (app initialization, config loading) ...

    # Initialize extensions
    # ... (mongo, login_manager, etc.) ...

    # Add now() to Jinja globals
    # ... (context_processor) ...

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.tickets import tickets_bp
    from .routes.admin import admin_bp  # <-- IMPORT admin blueprint

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp) # <-- REGISTER admin blueprint

    # Error Handlers
    # ... (404, 500 handlers) ...

    app.logger.info("Help Desk App Initialized with Admin Panel")
    return app