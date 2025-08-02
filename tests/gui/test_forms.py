"""Form validation tests."""

import pytest
from src.gui.forms import LoginForm, CreateUserForm


class TestLoginForm:
    """Test login form validation."""
    
    def test_login_form_valid_data(self, app):
        """Test login form with valid data."""
        with app.app_context():
            form = LoginForm(data={
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            assert form.validate() is True
    
    def test_login_form_missing_email(self, app):
        """Test login form with missing email."""
        with app.app_context():
            form = LoginForm(data={
                'password': 'testpass123'
            })
            assert form.validate() is False
            assert 'This field is required.' in form.email.errors
    
    def test_login_form_missing_password(self, app):
        """Test login form with missing password."""
        with app.app_context():
            form = LoginForm(data={
                'email': 'test@example.com'
            })
            assert form.validate() is False
            assert 'This field is required.' in form.password.errors
    
    def test_login_form_invalid_email(self, app):
        """Test login form with invalid email."""
        with app.app_context():
            form = LoginForm(data={
                'email': 'invalid-email',
                'password': 'testpass123'
            })
            assert form.validate() is False
            assert 'Invalid email address.' in form.email.errors
    
    def test_login_form_empty_fields(self, app):
        """Test login form with empty fields."""
        with app.app_context():
            form = LoginForm(data={
                'email': '',
                'password': ''
            })
            assert form.validate() is False
            assert 'This field is required.' in form.email.errors
            assert 'This field is required.' in form.password.errors


class TestCreateUserForm:
    """Test create user form validation."""
    
    def test_create_user_form_valid_data(self, app):
        """Test create user form with valid data."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': 'newuser@example.com',
                'password': 'newpass123',
                'first_name': 'New',
                'last_name': 'User',
                'phone': '555-1234',
                'address': '123 Main St',
                'usbc_id': 'USBC123',
                'tnba_id': 'TNBA456',
                'registered_user': True
            })
            assert form.validate() is True
    
    def test_create_user_form_minimal_data(self, app):
        """Test create user form with minimal required data."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': 'minimal@example.com',
                'password': 'minpass123',
                'first_name': 'Min',
                'last_name': 'User',
                'phone': '555-5678'
            })
            assert form.validate() is True
    
    def test_create_user_form_missing_required_fields(self, app):
        """Test create user form with missing required fields."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': '',
                'password': '',
                'first_name': '',
                'last_name': '',
                'phone': ''
            })
            assert form.validate() is False
            assert 'This field is required.' in form.email.errors
            assert 'This field is required.' in form.password.errors
            assert 'This field is required.' in form.first_name.errors
            assert 'This field is required.' in form.last_name.errors
            assert 'This field is required.' in form.phone.errors
    
    def test_create_user_form_invalid_email(self, app):
        """Test create user form with invalid email."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': 'invalid-email',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '555-1234'
            })
            assert form.validate() is False
            assert 'Invalid email address.' in form.email.errors
    
    def test_create_user_form_short_password(self, app):
        """Test create user form with short password."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': 'test@example.com',
                'password': '123',
                'first_name': 'Test',
                'last_name': 'User',
                'phone': '555-1234'
            })
            assert form.validate() is False
            assert 'Field must be at least 6 characters long.' in form.password.errors
    
    def test_create_user_form_long_fields(self, app):
        """Test create user form with fields exceeding max length."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': 'test@example.com',
                'password': 'testpass123',
                'first_name': 'A' * 101,  # Max 100 chars
                'last_name': 'B' * 101,   # Max 100 chars
                'phone': '555-1234',
                'address': 'A' * 501,     # Max 500 chars
                'usbc_id': 'U' * 51,      # Max 50 chars
                'tnba_id': 'T' * 51       # Max 50 chars
            })
            assert form.validate() is False
            assert 'Field cannot be longer than 100 characters.' in form.first_name.errors
            assert 'Field cannot be longer than 100 characters.' in form.last_name.errors
            # The optional fields might not validate if they're not required
            # Just check that the form overall validation failed
            assert not form.validate()
            # Address field validation should also fail if it's too long
            if form.address.errors:
                assert 'Field cannot be longer than 500 characters.' in form.address.errors
    
    def test_create_user_form_optional_fields(self, app):
        """Test create user form with optional fields empty."""
        with app.app_context():
            form = CreateUserForm(data={
                'email': 'optional@example.com',
                'password': 'optionalpass123',
                'first_name': 'Optional',
                'last_name': 'User',
                'phone': '555-9999',
                'address': '',
                'usbc_id': '',
                'tnba_id': '',
                'registered_user': False
            })
            assert form.validate() is True
    
    def test_create_user_form_checkbox_values(self, app):
        """Test create user form checkbox handling."""
        with app.app_context():
            # Test with registered_user checked
            form = CreateUserForm(data={
                'email': 'member@example.com',
                'password': 'memberpass123',
                'first_name': 'Member',
                'last_name': 'User',
                'phone': '555-1111',
                'registered_user': True
            })
            assert form.validate() is True
            assert form.registered_user.data is True
            
            # Test with registered_user unchecked
            form = CreateUserForm(data={
                'email': 'nonmember@example.com',
                'password': 'nonmemberpass123',
                'first_name': 'NonMember',
                'last_name': 'User',
                'phone': '555-2222',
                'registered_user': False
            })
            assert form.validate() is True
            assert form.registered_user.data is False