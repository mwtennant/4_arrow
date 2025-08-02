"""Utility functions for the GUI application."""

from functools import wraps
from typing import Optional, Callable, Any
from flask import session, redirect, url_for, flash

from core.models import User
from storage.database import db_manager


def get_current_user() -> Optional[User]:
    """Get the current user from the session.
    
    Returns:
        User object if logged in, None otherwise.
    """
    if 'user_id' not in session:
        return None
    
    db_session = db_manager.get_session()
    try:
        user = db_session.query(User).filter(User.id == session['user_id']).first()
        return user
    except Exception:
        return None
    finally:
        db_session.close()


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for a route.
    
    Args:
        f: The function to decorate.
        
    Returns:
        Decorated function that checks authentication.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function