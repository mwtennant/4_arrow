"""Main Flask application and route definitions."""

from flask import Flask, render_template, session, redirect, url_for, request, flash
from typing import Optional

from core.auth import auth_manager, AuthenticationError
from core.models import User
from storage.database import db_manager
from .utils import get_current_user


def create_app() -> Flask:
    """Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object('src.gui.config.Config')
    
    # Initialize database
    db_manager.create_tables()
    
    # Register blueprints
    from .auth import auth_bp
    from .users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    @app.route('/')
    def index() -> str:
        """Landing page route.
        
        Returns:
            Rendered template for the landing page.
        """
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Get user from session
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        
        return render_template('index.html', user=user)
    
    @app.errorhandler(404)
    def not_found(error) -> tuple[str, int]:
        """Handle 404 errors.
        
        Args:
            error: The error object.
            
        Returns:
            Rendered error template and 404 status code.
        """
        return render_template('error.html', 
                             error_title="Page Not Found",
                             error_message="The page you are looking for does not exist."), 404
    
    @app.errorhandler(500)
    def internal_error(error) -> tuple[str, int]:
        """Handle 500 errors.
        
        Args:
            error: The error object.
            
        Returns:
            Rendered error template and 500 status code.
        """
        return render_template('error.html',
                             error_title="Internal Server Error",
                             error_message="Something went wrong on our end. Please try again later."), 500
    
    return app




if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)