"""Tests for CLI commands."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from main import cli
from core.auth import AuthenticationError
from core.models import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


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


class TestCreateUserCLI:
    """Test cases for the create user CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_success_with_required_args(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test successful user creation with required arguments only."""
        mock_user = User(
            first_name="Bob",
            last_name="Lane",
            email=None,
        )
        mock_create_user.return_value = mock_user
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Bob',
            '--last', 'Lane'
        ])
        
        assert result.exit_code == 0
        assert "User created successfully: Bob Lane" in result.output
        mock_validate.assert_called_once_with("Bob", "Lane")
        mock_create_user.assert_called_once_with(
            first="Bob",
            last="Lane",
            address=None,
            usbc_id=None,
            tnba_id=None,
            phone=None,
            email=None
        )
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_success_with_email(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test successful user creation with email."""
        mock_user = User(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
        )
        mock_create_user.return_value = mock_user
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Alice',
            '--last', 'Smith',
            '--email', 'alice@example.com'
        ])
        
        assert result.exit_code == 0
        assert "User created successfully: Alice Smith (alice@example.com)" in result.output
        mock_validate.assert_called_once_with("Alice", "Smith")
        mock_create_user.assert_called_once_with(
            first="Alice",
            last="Smith",
            address=None,
            usbc_id=None,
            tnba_id=None,
            phone=None,
            email="alice@example.com"
        )
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_success_with_all_args(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test successful user creation with all arguments."""
        mock_user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-1234",
            address="123 Main St",
            usbc_id="12345",
            tnba_id="67890",
        )
        mock_create_user.return_value = mock_user
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'John',
            '--last', 'Doe',
            '--email', 'john@example.com',
            '--phone', '555-1234',
            '--address', '123 Main St',
            '--usbc_id', '12345',
            '--tnba_id', '67890'
        ])
        
        assert result.exit_code == 0
        assert "User created successfully: John Doe (john@example.com)" in result.output
        mock_validate.assert_called_once_with("John", "Doe")
        mock_create_user.assert_called_once_with(
            first="John",
            last="Doe",
            address="123 Main St",
            usbc_id="12345",
            tnba_id="67890",
            phone="555-1234",
            email="john@example.com"
        )
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_duplicate_email_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with duplicate email error."""
        mock_create_user.side_effect = IntegrityError("Email already exists", None, None)
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Alice',
            '--last', 'Smith',
            '--email', 'alice@example.com'
        ])
        
        assert result.exit_code == 2
        assert "ERROR: Email already exists. Try using get-profile to find the existing user." in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_duplicate_usbc_id_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with duplicate USBC ID error."""
        mock_create_user.side_effect = IntegrityError("USBC ID already exists", None, None)
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Bob',
            '--last', 'Lane',
            '--usbc_id', '12345'
        ])
        
        assert result.exit_code == 2
        assert "ERROR: USBC ID already exists in the database." in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_duplicate_tnba_id_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with duplicate TNBA ID error."""
        mock_create_user.side_effect = IntegrityError("TNBA ID already exists", None, None)
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Charlie',
            '--last', 'Brown',
            '--tnba_id', '67890'
        ])
        
        assert result.exit_code == 2
        assert "ERROR: TNBA ID already exists in the database." in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_generic_integrity_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with generic integrity error."""
        mock_create_user.side_effect = IntegrityError("Some other constraint violation", None, None)
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Test',
            '--last', 'User'
        ])
        
        assert result.exit_code == 1
        assert "ERROR:" in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_database_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with database error."""
        mock_create_user.side_effect = SQLAlchemyError("Database connection failed")
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Test',
            '--last', 'User'
        ])
        
        assert result.exit_code == 1
        assert "ERROR: Database error occurred:" in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_unexpected_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with unexpected error."""
        mock_create_user.side_effect = Exception("Unexpected error")
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Test',
            '--last', 'User'
        ])
        
        assert result.exit_code == 1
        assert "ERROR: An unexpected error occurred: Unexpected error" in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_first_name_validation_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with first name validation error."""
        mock_create_user.side_effect = ValueError("First name cannot be empty")
        
        result = runner.invoke(cli, [
            'create',
            '--first', '',
            '--last', 'User'
        ])
        
        assert result.exit_code == 3
        assert "ERROR: First name cannot be empty" in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_last_name_validation_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with last name validation error."""
        mock_create_user.side_effect = ValueError("Last name cannot be empty")
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Test',
            '--last', ''
        ])
        
        assert result.exit_code == 3
        assert "ERROR: Last name cannot be empty" in result.output
    
    @patch('main.create_user')
    @patch('main.validate_create_args')
    @patch('main.db_manager')
    def test_create_user_generic_value_error(self, mock_db_manager, mock_validate, mock_create_user, runner):
        """Test create user with generic value error."""
        mock_create_user.side_effect = ValueError("Some other validation error")
        
        result = runner.invoke(cli, [
            'create',
            '--first', 'Test',
            '--last', 'User'
        ])
        
        assert result.exit_code == 1
        assert "ERROR: Some other validation error" in result.output