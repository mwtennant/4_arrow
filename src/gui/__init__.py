"""GUI package initialization and app factory."""

from flask import Flask
from .config import Config


def create_app() -> Flask:
    """Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    from .auth import auth_bp
    from .users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    # Register main routes
    from . import app as main_routes
    
    return app