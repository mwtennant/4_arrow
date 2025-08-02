"""Configuration settings for the GUI application."""

import os
from typing import Optional


class Config:
    """Configuration class for Flask application."""
    
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_URL: Optional[str] = os.environ.get('DATABASE_URL', 'sqlite:///tournament_control.db')
    
    # Flask-WTF settings
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int = 3600  # 1 hour
    
    # Session settings
    SESSION_COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    PERMANENT_SESSION_LIFETIME: int = 3600  # 1 hour