"""Clean tests for CLI functionality."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from main import cli
from core.models import User


class TestCLICommands:
    """Test CLI command functionality."""
    
    def test_cli_help(self):
        """Test that CLI help is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "4th Arrow Tournament Control CLI" in result.output
    
    def test_signup_command_help(self):
        """Test signup command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['signup', '--help'])
        
        assert result.exit_code == 0
        assert "Sign up a new user account" in result.output
    
    def test_login_command_help(self):
        """Test login command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['login', '--help'])
        
        assert result.exit_code == 0
        assert "Log in with email and password" in result.output
    
    def test_create_command_help(self):
        """Test create command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create', '--help'])
        
        assert result.exit_code == 0
        assert "Create a new user" in result.output
    
    def test_list_users_command_help(self):
        """Test list-users command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list-users', '--help'])
        
        assert result.exit_code == 0
        assert "List users with enhanced filtering" in result.output
        assert "--role" in result.output
        assert "--member" in result.output  # Legacy flag should be shown
    
    @patch('main.auth_manager.create_user')
    @patch('main.db_manager.get_session')
    def test_signup_command_success(self, mock_get_session, mock_create_user):
        """Test successful signup command."""
        # Mock session and user creation
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        mock_create_user.return_value = mock_user
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'signup',
            '--email', 'test@example.com',
            '--password', 'password123',
            '--first', 'Test',
            '--last', 'User',
            '--phone', '555-1234'
        ])
        
        assert result.exit_code == 0
        assert "User account created successfully" in result.output
        assert "test@example.com" in result.output
        
        # Verify the auth manager was called correctly
        mock_create_user.assert_called_once()
        call_args = mock_create_user.call_args
        assert call_args.kwargs['email'] == 'test@example.com'
        assert call_args.kwargs['first_name'] == 'Test'
        assert call_args.kwargs['last_name'] == 'User'
    
    @patch('main.auth_manager.authenticate_user')
    @patch('main.db_manager.get_session')
    def test_login_command_success(self, mock_get_session, mock_authenticate_user):
        """Test successful login command."""
        # Mock session and authentication
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        mock_authenticate_user.return_value = mock_user
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'login',
            '--email', 'test@example.com',
            '--password', 'password123'
        ])
        
        assert result.exit_code == 0
        assert "Login successful" in result.output
        assert "Welcome, Test User!" in result.output
        
        # Verify authentication was called
        mock_authenticate_user.assert_called_once_with(
            mock_session, 'test@example.com', 'password123'
        )
    
    @patch('src.commands.create.create_user')
    def test_create_command_success(self, mock_create_user):
        """Test successful create command."""
        # Mock user creation
        mock_user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        mock_user.id = 1
        mock_create_user.return_value = mock_user
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create',
            '--first', 'John',
            '--last', 'Doe',
            '--email', 'john@example.com'
        ])
        
        assert result.exit_code == 0
        assert "User created successfully" in result.output
        assert "John Doe" in result.output
        assert "john@example.com" in result.output
        
        # Verify create_user was called with correct parameters
        mock_create_user.assert_called_once_with(
            first='John',
            last='Doe',
            address=None,
            usbc_id=None,
            tnba_id=None,
            phone=None,
            email='john@example.com'
        )
    
    def test_create_command_missing_required_fields(self):
        """Test create command with missing required fields."""
        runner = CliRunner()
        
        # Missing last name
        result = runner.invoke(cli, [
            'create',
            '--first', 'John'
        ])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output or "Usage:" in result.output


class TestCLIRoleFlags:
    """Test CLI role flag functionality - integration with our role refactor."""
    
    @patch('src.commands.list_users.list_users_enhanced')
    @patch('utils.csv_writer.validate_csv_path')
    @patch('src.commands.list_users.parse_date_filter')
    def test_role_flag_works(self, mock_parse_date, mock_validate_csv, mock_list_users):
        """Test that --role flag works correctly."""
        mock_list_users.return_value = []
        
        runner = CliRunner()
        result = runner.invoke(cli, ['list-users', '--role', 'registered_user'])
        
        assert result.exit_code == 0
        mock_list_users.assert_called_once()
        
        # Check that role was passed correctly
        call_args = mock_list_users.call_args
        assert call_args.kwargs['role'].value == 'registered_user'
    
    @patch('src.commands.list_users.list_users_enhanced')
    @patch('utils.csv_writer.validate_csv_path')
    @patch('src.commands.list_users.parse_date_filter')
    def test_member_flag_shows_deprecation_warning(self, mock_parse_date, mock_validate_csv, mock_list_users):
        """Test that --member flag shows deprecation warning."""
        mock_list_users.return_value = []
        
        runner = CliRunner()
        
        # Capture stderr to see the warning
        result = runner.invoke(cli, ['list-users', '--member'])
        
        assert result.exit_code == 0
        mock_list_users.assert_called_once()
        
        # Check that it was converted to registered_user
        call_args = mock_list_users.call_args
        assert call_args.kwargs['role'].value == 'registered_user'
    
    def test_both_role_flags_error(self):
        """Test that using both --role and --member flags returns error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list-users', '--role', 'registered_user', '--member'])
        
        assert result.exit_code == 4
        assert "Cannot use both --member and --role flags" in result.output


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def test_all_commands_have_help(self):
        """Test that all commands have help text."""
        runner = CliRunner()
        
        # Get list of commands
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        
        # Check that main commands are present
        commands_to_check = ['signup', 'login', 'create', 'list-users', 'merge']
        
        for command in commands_to_check:
            if command in result.output:
                # Test help for this command
                help_result = runner.invoke(cli, [command, '--help'])
                assert help_result.exit_code == 0, f"Help failed for {command}"
                assert command in help_result.output, f"Command name not in help for {command}"
    
    def test_cli_database_initialization(self):
        """Test that CLI initializes database tables."""
        runner = CliRunner()
        
        with patch('main.db_manager.create_tables') as mock_create_tables:
            # Any command should trigger table creation
            result = runner.invoke(cli, ['--help'])
            
            assert result.exit_code == 0
            mock_create_tables.assert_called_once()