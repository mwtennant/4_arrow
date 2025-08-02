"""Application and route tests."""

import pytest
from flask import url_for


class TestAppRoutes:
    """Test main application routes."""
    
    def test_index_redirects_to_login_when_not_authenticated(self, client):
        """Test that index redirects to login when not authenticated."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_index_shows_dashboard_when_authenticated(self, authenticated_client, test_user):
        """Test that index shows dashboard when authenticated."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Hello Test, what are you testing now?' in response.data
    
    def test_404_error_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data
    
    def test_dashboard_content(self, authenticated_client):
        """Test dashboard content and navigation."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'User Management' in response.data
        assert b'Organizations' in response.data
        assert b'Tournaments' in response.data
        assert b'Settings' in response.data


class TestAppUtilities:
    """Test application utility functions."""
    
    def test_get_current_user_returns_none_when_not_logged_in(self, app):
        """Test get_current_user returns None when not logged in."""
        with app.test_request_context():
            from src.gui.utils import get_current_user
            user = get_current_user()
            assert user is None
    
    def test_get_current_user_returns_user_when_logged_in(self, app, test_user):
        """Test get_current_user returns user when logged in."""
        with app.test_request_context():
            with app.test_client() as client:
                with client.session_transaction() as session:
                    session['user_id'] = test_user.id
                
                from src.gui.utils import get_current_user
                user = get_current_user()
                assert user is not None
                assert user.id == test_user.id
    
    def test_require_auth_decorator(self, client):
        """Test require_auth decorator redirects unauthenticated users."""
        # Try to access protected route
        response = client.get('/users/')
        assert response.status_code == 302
        assert '/auth/login' in response.location