"""Tests for remove organization user command."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from sqlalchemy.exc import IntegrityError

from src.commands.remove_org_user import (
    remove_users_from_organization,
    validate_organization_exists,
    validate_user_exists,
    check_user_membership,
    deduplicate_user_ids,
    remove_org_user_command
)
from core.models import Organization, User, OrganizationMembership
import click
from click.testing import CliRunner


class TestValidateOrganizationExists:
    """Test organization existence validation."""
    
    def test_validate_organization_exists_success(self):
        """Test successful organization validation."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_organization.name = "Test Org"
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_organization
        
        result = validate_organization_exists(mock_session, 1)
        
        assert result == mock_organization
        mock_session.query.assert_called_once_with(Organization)
    
    def test_validate_organization_exists_not_found(self):
        """Test organization not found raises ClickException."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        with pytest.raises(click.ClickException, match="Organization with ID 999 not found"):
            validate_organization_exists(mock_session, 999)


class TestValidateUserExists:
    """Test user existence validation."""
    
    def test_validate_user_exists_success(self):
        """Test successful user validation."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user
        
        result = validate_user_exists(mock_session, 123)
        
        assert result == mock_user
        mock_session.query.assert_called_once_with(User)
    
    def test_validate_user_exists_not_found(self):
        """Test user not found returns None."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = validate_user_exists(mock_session, 999)
        
        assert result is None


class TestCheckUserMembership:
    """Test user membership checking."""
    
    def test_check_user_membership_exists(self):
        """Test checking existing membership."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_membership = Mock(spec=OrganizationMembership)
        mock_membership.id = 1
        mock_membership.user_id = 123
        mock_membership.organization_id = 1
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_membership
        
        result = check_user_membership(mock_session, 123, 1)
        
        assert result == mock_membership
        mock_session.query.assert_called_once_with(OrganizationMembership)
    
    def test_check_user_membership_not_exists(self):
        """Test checking non-existing membership."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = check_user_membership(mock_session, 123, 1)
        
        assert result is None


class TestDeduplicateUserIds:
    """Test user ID deduplication."""
    
    def test_deduplicate_user_ids_no_duplicates(self):
        """Test deduplication with no duplicates."""
        user_ids = [1, 2, 3]
        result = deduplicate_user_ids(user_ids)
        assert result == [1, 2, 3]
    
    def test_deduplicate_user_ids_with_duplicates(self):
        """Test deduplication with duplicates."""
        user_ids = [1, 2, 2, 3, 1, 4]
        result = deduplicate_user_ids(user_ids)
        assert result == [1, 2, 3, 4]
    
    def test_deduplicate_user_ids_empty_list(self):
        """Test deduplication with empty list."""
        user_ids = []
        result = deduplicate_user_ids(user_ids)
        assert result == []
    
    def test_deduplicate_user_ids_single_item(self):
        """Test deduplication with single item."""
        user_ids = [5]
        result = deduplicate_user_ids(user_ids)
        assert result == [5]


class TestRemoveUsersFromOrganization:
    """Test removing users from organization."""
    
    @patch('src.commands.remove_org_user.db_manager')
    @patch('sys.exit')
    @patch('click.echo')
    def test_remove_users_empty_list(self, mock_echo, mock_exit, mock_db_manager):
        """Test removing users with empty list."""
        remove_users_from_organization(1, [])
        mock_echo.assert_called_once_with("Error: No user IDs provided", err=True)
        mock_exit.assert_called_once_with(5)
    
    @patch('src.commands.remove_org_user.db_manager')
    @patch('builtins.print')
    def test_remove_single_user_success(self, mock_print, mock_db_manager):
        """Test successfully removing single user."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        
        # Mock user exists
        mock_user = Mock(spec=User)
        mock_user.id = 123
        
        # Mock membership exists
        mock_membership = Mock(spec=OrganizationMembership)
        mock_membership.id = 1
        mock_membership.user_id = 123
        mock_membership.organization_id = 1
        
        with patch('src.commands.remove_org_user.validate_organization_exists', return_value=mock_organization), \
             patch('src.commands.remove_org_user.validate_user_exists', return_value=mock_user), \
             patch('src.commands.remove_org_user.check_user_membership', return_value=mock_membership), \
             patch('click.echo') as mock_echo:
            
            remove_users_from_organization(1, [123])
            
            # Verify membership was deleted
            mock_session.delete.assert_called_once_with(mock_membership)
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
            
            # Verify success message
            mock_echo.assert_called_with("User 123 successfully removed from organization 1")
    
    @patch('src.commands.remove_org_user.db_manager')
    def test_remove_multiple_users_success(self, mock_db_manager):
        """Test successfully removing multiple users."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        
        # Mock users exist
        mock_user1 = Mock(spec=User)
        mock_user1.id = 123
        mock_user2 = Mock(spec=User)
        mock_user2.id = 456
        
        # Mock memberships exist
        mock_membership1 = Mock(spec=OrganizationMembership)
        mock_membership1.id = 1
        mock_membership1.user_id = 123
        mock_membership1.organization_id = 1
        
        mock_membership2 = Mock(spec=OrganizationMembership)
        mock_membership2.id = 2
        mock_membership2.user_id = 456
        mock_membership2.organization_id = 1
        
        with patch('src.commands.remove_org_user.validate_organization_exists', return_value=mock_organization), \
             patch('src.commands.remove_org_user.validate_user_exists', side_effect=[mock_user1, mock_user2]), \
             patch('src.commands.remove_org_user.check_user_membership', side_effect=[mock_membership1, mock_membership2]), \
             patch('click.echo') as mock_echo:
            
            remove_users_from_organization(1, [123, 456])
            
            # Verify memberships were deleted
            assert mock_session.delete.call_count == 2
            mock_session.delete.assert_any_call(mock_membership1)
            mock_session.delete.assert_any_call(mock_membership2)
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
            
            # Verify success messages
            mock_echo.assert_any_call("Successfully removed the following users from organization 1:")
            mock_echo.assert_any_call("- User 123")
            mock_echo.assert_any_call("- User 456")
    
    @patch('src.commands.remove_org_user.db_manager')
    def test_remove_users_partial_success(self, mock_db_manager):
        """Test partial success - some users removed, some skipped."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        
        # Mock users - one exists, one doesn't
        mock_user1 = Mock(spec=User)
        mock_user1.id = 123
        
        # Mock membership - only for first user
        mock_membership1 = Mock(spec=OrganizationMembership)
        mock_membership1.id = 1
        mock_membership1.user_id = 123
        mock_membership1.organization_id = 1
        
        with patch('src.commands.remove_org_user.validate_organization_exists', return_value=mock_organization), \
             patch('src.commands.remove_org_user.validate_user_exists', side_effect=[mock_user1, None]), \
             patch('src.commands.remove_org_user.check_user_membership', return_value=mock_membership1), \
             patch('click.echo') as mock_echo:
            
            remove_users_from_organization(1, [123, 999])
            
            # Verify first membership was deleted
            mock_session.delete.assert_called_once_with(mock_membership1)
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
            
            # Verify success and skip messages
            mock_echo.assert_any_call("User 123 successfully removed from organization 1")
            mock_echo.assert_any_call("Skipped the following users:")
            mock_echo.assert_any_call("- User 999: User not found")
    
    @patch('src.commands.remove_org_user.db_manager')
    def test_remove_users_not_members(self, mock_db_manager):
        """Test skipping users who are not members."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        
        # Mock user exists but is not a member
        mock_user = Mock(spec=User)
        mock_user.id = 123
        
        with patch('src.commands.remove_org_user.validate_organization_exists', return_value=mock_organization), \
             patch('src.commands.remove_org_user.validate_user_exists', return_value=mock_user), \
             patch('src.commands.remove_org_user.check_user_membership', return_value=None), \
             patch('click.echo') as mock_echo:
            
            remove_users_from_organization(1, [123])
            
            # Verify no membership was deleted
            mock_session.delete.assert_not_called()
            mock_session.commit.assert_not_called()
            mock_session.close.assert_called_once()
            
            # Verify skip message
            mock_echo.assert_any_call("Skipped the following users:")
            mock_echo.assert_any_call("- User 123: Not a member of organization 1")
    
    @patch('src.commands.remove_org_user.db_manager')
    @patch('sys.exit')
    def test_remove_users_organization_not_found(self, mock_exit, mock_db_manager):
        """Test organization not found raises ClickException."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        with patch('src.commands.remove_org_user.validate_organization_exists', 
                   side_effect=click.ClickException("Organization with ID 999 not found")):
            
            with pytest.raises(click.ClickException):
                remove_users_from_organization(999, [123])
    
    @patch('src.commands.remove_org_user.db_manager')
    def test_remove_users_with_duplicates(self, mock_db_manager):
        """Test removing users with duplicate IDs."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        
        # Mock user exists
        mock_user = Mock(spec=User)
        mock_user.id = 123
        
        # Mock membership exists
        mock_membership = Mock(spec=OrganizationMembership)
        mock_membership.id = 1
        mock_membership.user_id = 123
        mock_membership.organization_id = 1
        
        with patch('src.commands.remove_org_user.validate_organization_exists', return_value=mock_organization), \
             patch('src.commands.remove_org_user.validate_user_exists', return_value=mock_user), \
             patch('src.commands.remove_org_user.check_user_membership', return_value=mock_membership), \
             patch('click.echo') as mock_echo:
            
            # Pass duplicate user IDs
            remove_users_from_organization(1, [123, 123, 123])
            
            # Verify membership was deleted only once (deduplication worked)
            mock_session.delete.assert_called_once_with(mock_membership)
            mock_session.commit.assert_called_once()
            
            # Verify success message for single user (due to deduplication)
            mock_echo.assert_called_with("User 123 successfully removed from organization 1")
    
    @patch('src.commands.remove_org_user.db_manager')
    @patch('sys.exit')
    def test_remove_users_database_error(self, mock_exit, mock_db_manager):
        """Test database error handling during commit."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        
        # Mock user exists
        mock_user = Mock(spec=User)
        mock_user.id = 123
        
        # Mock membership exists
        mock_membership = Mock(spec=OrganizationMembership)
        mock_membership.id = 1
        mock_membership.user_id = 123
        mock_membership.organization_id = 1
        
        # Mock commit raises IntegrityError
        mock_session.commit.side_effect = IntegrityError("statement", "params", "orig")
        
        with patch('src.commands.remove_org_user.validate_organization_exists', return_value=mock_organization), \
             patch('src.commands.remove_org_user.validate_user_exists', return_value=mock_user), \
             patch('src.commands.remove_org_user.check_user_membership', return_value=mock_membership), \
             patch('click.echo') as mock_echo:
            
            remove_users_from_organization(1, [123])
            
            # Verify rollback was called
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
            
            # Verify error message and exit (match the actual SQLAlchemy error format)
            error_calls = [call for call in mock_echo.call_args_list if call.kwargs.get('err') is True]
            assert len(error_calls) > 0
            assert "Database constraint violation" in error_calls[0].args[0]
            mock_exit.assert_called_with(1)


class TestRemoveOrgUserCommand:
    """Test the CLI command interface."""
    
    def test_remove_org_user_command_success(self):
        """Test successful command execution."""
        runner = CliRunner()
        
        with patch('src.commands.remove_org_user.remove_users_from_organization') as mock_remove:
            result = runner.invoke(
                remove_org_user_command,
                ['--organization-id', '1', '--user-id', '123']
            )
            
            assert result.exit_code == 0
            mock_remove.assert_called_once_with(
                organization_id=1,
                user_ids=[123]
            )
    
    def test_remove_org_user_command_multiple_users(self):
        """Test command with multiple users."""
        runner = CliRunner()
        
        with patch('src.commands.remove_org_user.remove_users_from_organization') as mock_remove:
            result = runner.invoke(
                remove_org_user_command,
                ['--organization-id', '1', '--user-id', '123', '--user-id', '456', '--user-id', '789']
            )
            
            assert result.exit_code == 0
            mock_remove.assert_called_once_with(
                organization_id=1,
                user_ids=[123, 456, 789]
            )
    
    def test_remove_org_user_command_with_force_flag(self):
        """Test command with force flag."""
        runner = CliRunner()
        
        with patch('src.commands.remove_org_user.remove_users_from_organization') as mock_remove:
            result = runner.invoke(
                remove_org_user_command,
                ['--organization-id', '1', '--user-id', '123', '--force']
            )
            
            assert result.exit_code == 0
            mock_remove.assert_called_once_with(
                organization_id=1,
                user_ids=[123]
            )
    
    def test_remove_org_user_command_missing_organization_id(self):
        """Test command missing organization ID."""
        runner = CliRunner()
        
        result = runner.invoke(
            remove_org_user_command,
            ['--user-id', '123']
        )
        
        assert result.exit_code == 2  # Click's missing option exit code
        assert "Missing option '--organization-id'" in result.output
    
    def test_remove_org_user_command_missing_user_id(self):
        """Test command missing user ID."""
        runner = CliRunner()
        
        result = runner.invoke(
            remove_org_user_command,
            ['--organization-id', '1']
        )
        
        assert result.exit_code == 2  # Click's missing option exit code
        assert "Missing option '--user-id'" in result.output
    
    def test_remove_org_user_command_organization_not_found(self):
        """Test command with organization not found."""
        runner = CliRunner()
        
        with patch('src.commands.remove_org_user.remove_users_from_organization',
                   side_effect=click.ClickException("Organization with ID 999 not found")) as mock_remove:
            result = runner.invoke(
                remove_org_user_command,
                ['--organization-id', '999', '--user-id', '123']
            )
            
            assert result.exit_code == 2
            assert "Organization with ID 999 not found" in result.output
    
    def test_remove_org_user_command_unexpected_error(self):
        """Test command with unexpected error."""
        runner = CliRunner()
        
        with patch('src.commands.remove_org_user.remove_users_from_organization',
                   side_effect=Exception("Database connection failed")) as mock_remove:
            result = runner.invoke(
                remove_org_user_command,
                ['--organization-id', '1', '--user-id', '123']
            )
            
            assert result.exit_code == 1
            assert "An unexpected error occurred: Database connection failed" in result.output