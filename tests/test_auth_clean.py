"""Clean tests for authentication functionality."""

import pytest
from unittest.mock import MagicMock, patch

from core.auth import AuthManager, AuthenticationError
from core.models import User


class TestAuthManager:
    """Test authentication manager functionality."""
    
    def test_validate_email_valid_cases(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk", 
            "admin@tournamentorg.com",
            "simple@test.com"
        ]
        
        for email in valid_emails:
            assert AuthManager.validate_email(email) is True
    
    def test_validate_email_invalid_cases(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "",
            "   ",
            None,
            "invalid-email",
            "@domain.com",
            "user@",
            "user space@example.com"
        ]
        
        for email in invalid_emails:
            assert AuthManager.validate_email(email) is False
    
    def test_validate_password_valid_cases(self):
        """Test password validation with valid passwords."""
        valid_passwords = [
            "password123",
            "123456",
            "a very long password",
            "P@ssw0rd!"
        ]
        
        for password in valid_passwords:
            assert AuthManager.validate_password(password) is True
    
    def test_validate_password_invalid_cases(self):
        """Test password validation with invalid passwords."""
        invalid_passwords = [
            "",
            "   ",
            None,
            "short",  # Less than 6 characters
            "12345"   # Less than 6 characters
        ]
        
        for password in invalid_passwords:
            assert AuthManager.validate_password(password) is False
    
    def test_hash_password_creates_hash(self):
        """Test that password hashing creates a bcrypt hash."""
        password = "testpassword123"
        
        hashed = AuthManager.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 20  # Bcrypt hashes are long
        assert hashed != password  # Should be different from original
    
    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = AuthManager.hash_password(password)
        
        result = AuthManager.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = AuthManager.hash_password(password)
        
        result = AuthManager.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_create_user_success(self):
        """Test successful user creation."""
        # Mock session
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Create user
        user = AuthManager.create_user(
            session=mock_session,
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            phone="555-1234"
        )
        
        # Verify user creation
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone == "555-1234"
        assert user.password_hash is not None
        assert user.password_hash != "password123"  # Should be hashed
        
        # Verify database interactions
        mock_session.add.assert_called_once_with(user)
        mock_session.commit.assert_called_once()
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        # Mock session to return existing user
        mock_session = MagicMock()
        existing_user = User(email="test@example.com")
        mock_session.query.return_value.filter_by.return_value.first.return_value = existing_user
        
        # Should raise authentication error
        with pytest.raises(AuthenticationError) as exc_info:
            AuthManager.create_user(
                session=mock_session,
                email="test@example.com",
                password="password123",
                first_name="Test",
                last_name="User",
                phone="555-1234"
            )
        
        assert "Email already registered" in str(exc_info.value)
    
    def test_create_user_invalid_email(self):
        """Test user creation with invalid email."""
        mock_session = MagicMock()
        
        with pytest.raises(AuthenticationError) as exc_info:
            AuthManager.create_user(
                session=mock_session,
                email="invalid-email",
                password="password123",
                first_name="Test",
                last_name="User",
                phone="555-1234"
            )
        
        assert "Invalid email address" in str(exc_info.value)
    
    def test_create_user_invalid_password(self):
        """Test user creation with invalid password."""
        mock_session = MagicMock()
        
        with pytest.raises(AuthenticationError) as exc_info:
            AuthManager.create_user(
                session=mock_session,
                email="test@example.com",
                password="short",  # Too short
                first_name="Test",
                last_name="User",
                phone="555-1234"
            )
        
        assert "Password must be at least 6 characters" in str(exc_info.value)
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Create a user with known password
        password = "testpassword123"
        hashed_password = AuthManager.hash_password(password)
        
        mock_user = User(
            email="test@example.com",
            password_hash=hashed_password,
            first_name="Test",
            last_name="User"
        )
        
        # Mock session
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        # Authenticate
        authenticated_user = AuthManager.authenticate_user(
            session=mock_session,
            email="test@example.com",
            password=password
        )
        
        assert authenticated_user == mock_user
        assert authenticated_user.email == "test@example.com"
    
    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        # Mock session to return no user
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with pytest.raises(AuthenticationError) as exc_info:
            AuthManager.authenticate_user(
                session=mock_session,
                email="nonexistent@example.com",
                password="password123"
            )
        
        assert "Invalid email or password" in str(exc_info.value)
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        # Create user with known password
        correct_password = "correctpassword"
        hashed_password = AuthManager.hash_password(correct_password)
        
        mock_user = User(
            email="test@example.com",
            password_hash=hashed_password
        )
        
        # Mock session
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        # Try to authenticate with wrong password
        with pytest.raises(AuthenticationError) as exc_info:
            AuthManager.authenticate_user(
                session=mock_session,
                email="test@example.com",
                password="wrongpassword"
            )
        
        assert "Invalid email or password" in str(exc_info.value)
    
    def test_authenticate_user_invalid_email(self):
        """Test authentication with invalid email format."""
        mock_session = MagicMock()
        
        with pytest.raises(AuthenticationError) as exc_info:
            AuthManager.authenticate_user(
                session=mock_session,
                email="invalid-email",
                password="password123"
            )
        
        assert "Invalid email address" in str(exc_info.value)