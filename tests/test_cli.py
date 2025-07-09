"""Tests for CLI commands."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from main import cli
from core.auth import AuthenticationError
from core.models import User


class TestCLICommands:
    """Test cases for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_signup_success(self, mock_db_manager, mock_auth_manager, runner):
        """Test successful user signup."""
        mock_user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        mock_auth_manager.create_user.return_value = mock_user
        
        result = runner.invoke(cli, [
            'signup',
            '--email', 'test@example.com',
            '--password', 'password123',
            '--first', 'John',
            '--last', 'Doe',
            '--phone', '555-1234'
        ])
        
        assert result.exit_code == 0
        assert "User account created successfully for test@example.com" in result.output
        mock_auth_manager.create_user.assert_called_once_with(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            address=None,
            usbc_id=None,
            tnba_id=None
        )
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_signup_with_optional_fields(self, mock_db_manager, mock_auth_manager, runner):
        """Test user signup with optional fields."""
        mock_user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            address="123 Main St",
            usbc_id="12345",
            tnba_id="67890"
        )
        mock_auth_manager.create_user.return_value = mock_user
        
        result = runner.invoke(cli, [
            'signup',
            '--email', 'test@example.com',
            '--password', 'password123',
            '--first', 'John',
            '--last', 'Doe',
            '--phone', '555-1234',
            '--address', '123 Main St',
            '--usbc_id', '12345',
            '--tnba_id', '67890'
        ])
        
        assert result.exit_code == 0
        assert "User account created successfully for test@example.com" in result.output
        mock_auth_manager.create_user.assert_called_once_with(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            address="123 Main St",
            usbc_id="12345",
            tnba_id="67890"
        )
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_signup_duplicate_email(self, mock_db_manager, mock_auth_manager, runner):
        """Test signup with duplicate email."""
        mock_auth_manager.create_user.side_effect = AuthenticationError("Email already exists")
        
        result = runner.invoke(cli, [
            'signup',
            '--email', 'test@example.com',
            '--password', 'password123',
            '--first', 'John',
            '--last', 'Doe',
            '--phone', '555-1234'
        ])
        
        assert result.exit_code == 1
        assert "Error: Email already exists" in result.output
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_signup_validation_error(self, mock_db_manager, mock_auth_manager, runner):
        """Test signup with validation error."""
        mock_auth_manager.create_user.side_effect = AuthenticationError("Invalid email format")
        
        result = runner.invoke(cli, [
            'signup',
            '--email', 'invalid-email',
            '--password', 'password123',
            '--first', 'John',
            '--last', 'Doe',
            '--phone', '555-1234'
        ])
        
        assert result.exit_code == 1
        assert "Error: Invalid email format" in result.output
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_signup_missing_required_fields(self, mock_db_manager, mock_auth_manager, runner):
        """Test signup with missing required fields."""
        result = runner.invoke(cli, [
            'signup',
            '--email', 'test@example.com',
            '--password', 'password123'
            # Missing --first, --last, --phone
        ])
        
        assert result.exit_code == 2  # Click validation error
        assert "Missing option" in result.output
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_login_success(self, mock_db_manager, mock_auth_manager, runner):
        """Test successful user login."""
        mock_user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        mock_auth_manager.authenticate_user.return_value = mock_user
        
        result = runner.invoke(cli, [
            'login',
            '--email', 'test@example.com',
            '--password', 'password123'
        ])
        
        assert result.exit_code == 0
        assert "Login successful. Welcome, John Doe!" in result.output
        mock_auth_manager.authenticate_user.assert_called_once_with(
            "test@example.com",
            "password123"
        )
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_login_invalid_credentials(self, mock_db_manager, mock_auth_manager, runner):
        """Test login with invalid credentials."""
        mock_auth_manager.authenticate_user.side_effect = AuthenticationError("Invalid email or password")
        
        result = runner.invoke(cli, [
            'login',
            '--email', 'test@example.com',
            '--password', 'wrong_password'
        ])
        
        assert result.exit_code == 1
        assert "Error: Invalid email or password" in result.output
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_login_missing_credentials(self, mock_db_manager, mock_auth_manager, runner):
        """Test login with missing credentials."""
        result = runner.invoke(cli, [
            'login',
            '--email', 'test@example.com'
            # Missing --password
        ])
        
        assert result.exit_code == 2  # Click validation error
        assert "Missing option" in result.output
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_signup_unexpected_error(self, mock_db_manager, mock_auth_manager, runner):
        """Test signup with unexpected error."""
        mock_auth_manager.create_user.side_effect = Exception("Unexpected error")
        
        result = runner.invoke(cli, [
            'signup',
            '--email', 'test@example.com',
            '--password', 'password123',
            '--first', 'John',
            '--last', 'Doe',
            '--phone', '555-1234'
        ])
        
        assert result.exit_code == 1
        assert "An unexpected error occurred: Unexpected error" in result.output
    
    @patch('main.auth_manager')
    @patch('main.db_manager')
    def test_login_unexpected_error(self, mock_db_manager, mock_auth_manager, runner):
        """Test login with unexpected error."""
        mock_auth_manager.authenticate_user.side_effect = Exception("Unexpected error")
        
        result = runner.invoke(cli, [
            'login',
            '--email', 'test@example.com',
            '--password', 'password123'
        ])
        
        assert result.exit_code == 1
        assert "An unexpected error occurred: Unexpected error" in result.output