"""Test configuration and fixtures for GUI tests."""

import pytest
import tempfile
import os
from typing import Generator

from src.gui.app import create_app
from storage.database import DatabaseManager
from core.auth import auth_manager
from core.models import User, Base


@pytest.fixture
def app():
    """Create and configure a test app."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Setup test database manager
    test_db = DatabaseManager(f'sqlite:///{db_path}')
    test_db.create_tables()
    
    # Replace global db_manager for testing
    import storage.database
    import core.auth
    original_db_manager = storage.database.db_manager
    storage.database.db_manager = test_db
    core.auth.auth_manager = core.auth.AuthManager()
    
    # Create app with test config
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        yield app
    
    # Restore original db_manager
    storage.database.db_manager = original_db_manager
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app) -> User:
    """Create a test user."""
    with app.app_context():
        # Try to create user, if it exists, get the existing one
        try:
            user = auth_manager.create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User',
                phone='555-1234'
            )
        except Exception:
            # If user already exists, get it from database
            from storage.database import db_manager
            session = db_manager.get_session()
            try:
                user = session.query(User).filter(User.email == 'test@example.com').first()
                if not user:
                    # Create with different email if original doesn't exist
                    import uuid
                    unique_email = f'test-{uuid.uuid4().hex[:8]}@example.com'
                    user = auth_manager.create_user(
                        email=unique_email,
                        password='testpass123',
                        first_name='Test',
                        last_name='User',
                        phone='555-1234'
                    )
            finally:
                session.close()
        return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['user_name'] = f"{test_user.first_name} {test_user.last_name}"
    return client