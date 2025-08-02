"""Tests for authentication logic."""

import pytest
from unittest.mock import patch, MagicMock

from core.auth import AuthManager, AuthenticationError
from core.models import User
from storage.database import DatabaseManager


class TestAuthManager:
    """Test cases for AuthManager."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a test database manager."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.create_tables()
        return db_manager
    
    @pytest.fixture
    def session(self, db_manager):
        """Create a test database session."""
        session = db_manager.get_session()
        yield session
        session.close()
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@example.com"
        ]
        
        for email in valid_emails:
            assert AuthManager.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "",
            "   ",
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user@domain.",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            assert AuthManager.validate_email(email) is False
    
    def test_validate_password_valid(self):
        """Test password validation with valid passwords."""
        valid_passwords = [
            "password123",
            "123456",
            "a very long password",
            "P@ssw0rd!"
        ]
        
        for password in valid_passwords:
            assert AuthManager.validate_password(password) is True
    
    def test_validate_password_invalid(self):
        """Test password validation with invalid passwords."""
        invalid_passwords = [
            "",
            "   ",
            "123",
            "12345",
            "     "  # Only spaces
        ]
        
        for password in invalid_passwords:
            assert AuthManager.validate_password(password) is False
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password"
        hashed = AuthManager.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
    
    def test_verify_password(self):
        """Test password verification."""
        password = "test_password"
        hashed = AuthManager.hash_password(password)
        
        assert AuthManager.verify_password(password, hashed) is True
        assert AuthManager.verify_password("wrong_password", hashed) is False
    
    @patch('core.auth.db_manager')
    def test_create_user_success(self, mock_db_manager):
        """Test successful user creation."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        user = AuthManager.create_user(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('core.auth.db_manager')
    def test_create_user_duplicate_email(self, mock_db_manager):
        """Test user creation with duplicate email."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = User()
        
        with pytest.raises(AuthenticationError, match="Email already exists"):
            AuthManager.create_user(
                email="test@example.com",
                password="password123",
                first_name="John",
                last_name="Doe",
                phone="555-1234"
            )
    
    def test_create_user_validation_errors(self):
        """Test user creation with validation errors."""
        test_cases = [
            ("", "password123", "John", "Doe", "555-1234", "Email is required"),
            ("   ", "password123", "John", "Doe", "555-1234", "Email is required"),
            ("invalid-email", "password123", "John", "Doe", "555-1234", "Invalid email format"),
            ("test@example.com", "", "John", "Doe", "555-1234", "Password is required"),
            ("test@example.com", "   ", "John", "Doe", "555-1234", "Password is required"),
            ("test@example.com", "123", "John", "Doe", "555-1234", "Password must be at least 6 characters long"),
            ("test@example.com", "password123", "", "Doe", "555-1234", "First name is required"),
            ("test@example.com", "password123", "   ", "Doe", "555-1234", "First name is required"),
            ("test@example.com", "password123", "John", "", "555-1234", "Last name is required"),
            ("test@example.com", "password123", "John", "   ", "555-1234", "Last name is required"),
            ("test@example.com", "password123", "John", "Doe", "", "Phone number is required"),
            ("test@example.com", "password123", "John", "Doe", "   ", "Phone number is required"),
        ]
        
        for email, password, first_name, last_name, phone, expected_error in test_cases:
            with pytest.raises(AuthenticationError, match=expected_error):
                AuthManager.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                )
    
    @patch('core.auth.db_manager')
    def test_authenticate_user_success(self, mock_db_manager):
        """Test successful user authentication."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        password = "password123"
        hashed_password = AuthManager.hash_password(password)
        
        mock_user = User(
            email="test@example.com",
            password_hash=hashed_password,
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = AuthManager.authenticate_user("test@example.com", password)
        
        assert result == mock_user
        mock_session.close.assert_called_once()
    
    @patch('core.auth.db_manager')
    def test_authenticate_user_not_found(self, mock_db_manager):
        """Test authentication with non-existent user."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            AuthManager.authenticate_user("nonexistent@example.com", "password123")
    
    @patch('core.auth.db_manager')
    def test_authenticate_user_wrong_password(self, mock_db_manager):
        """Test authentication with wrong password."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        password = "password123"
        hashed_password = AuthManager.hash_password(password)
        
        mock_user = User(
            email="test@example.com",
            password_hash=hashed_password,
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            AuthManager.authenticate_user("test@example.com", "wrong_password")
    
    def test_authenticate_user_validation_errors(self):
        """Test authentication with validation errors."""
        test_cases = [
            ("", "password123", "Email is required"),
            ("   ", "password123", "Email is required"),
            ("test@example.com", "", "Password is required"),
            ("test@example.com", "   ", "Password is required"),
        ]
        
        for email, password, expected_error in test_cases:
            with pytest.raises(AuthenticationError, match=expected_error):
                AuthManager.authenticate_user(email, password)