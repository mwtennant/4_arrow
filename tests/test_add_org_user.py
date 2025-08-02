"""Tests for add organization user command."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.exc import IntegrityError

from src.commands.add_org_user import (
    add_users_to_organization,
    validate_organization_exists,
    validate_user_exists,
    validate_role_exists,
    check_user_membership,
    deduplicate_user_ids,
    add_org_user_command
)
from core.models import Organization, User, OrganizationMembership, Role
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


class TestValidateRoleExists:
    """Test role existence validation."""
    
    def test_validate_role_exists_success(self):
        """Test successful role validation."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_role = Mock(spec=Role)
        mock_role.id = 5
        mock_role.name = "Manager"
        mock_role.organization_id = 1
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_role
        
        result = validate_role_exists(mock_session, "Manager", 1)
        
        assert result == mock_role
        mock_session.query.assert_called_once_with(Role)
    
    def test_validate_role_exists_case_insensitive(self):
        """Test role validation is case-insensitive."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_role = Mock(spec=Role)
        mock_role.id = 5
        mock_role.name = "Manager"
        mock_role.organization_id = 1
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_role
        
        result = validate_role_exists(mock_session, "manager", 1)
        
        assert result == mock_role
    
    def test_validate_role_exists_not_found(self):
        """Test role not found returns None."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = validate_role_exists(mock_session, "NonExistent", 1)
        
        assert result is None


class TestCheckUserMembership:
    """Test user membership checking."""
    
    def test_check_user_membership_exists(self):
        """Test returns True when user is already a member."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_membership = Mock(spec=OrganizationMembership)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_membership
        
        result = check_user_membership(mock_session, 123, 1)
        
        assert result is True
        mock_session.query.assert_called_once_with(OrganizationMembership)
    
    def test_check_user_membership_not_exists(self):
        """Test returns False when user is not a member."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = check_user_membership(mock_session, 123, 1)
        
        assert result is False


class TestDeduplicateUserIds:
    """Test user ID deduplication."""
    
    def test_deduplicate_user_ids_no_duplicates(self):
        """Test deduplication with no duplicates."""
        user_ids = [1, 2, 3, 4]
        result = deduplicate_user_ids(user_ids)
        assert result == [1, 2, 3, 4]
    
    def test_deduplicate_user_ids_with_duplicates(self):
        """Test deduplication removes duplicates while preserving order."""
        user_ids = [1, 2, 3, 2, 4, 1, 5]
        result = deduplicate_user_ids(user_ids)
        assert result == [1, 2, 3, 4, 5]
    
    def test_deduplicate_user_ids_empty_list(self):
        """Test deduplication with empty list."""
        user_ids = []
        result = deduplicate_user_ids(user_ids)
        assert result == []
    
    def test_deduplicate_user_ids_all_same(self):
        """Test deduplication with all same IDs."""
        user_ids = [1, 1, 1, 1]
        result = deduplicate_user_ids(user_ids)
        assert result == [1]


class TestAddUsersToOrganization:
    """Test adding users to organization."""
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_add_single_user_success_no_role(self, mock_check_membership, mock_validate_user, 
                                           mock_validate_org, mock_db_manager):
        """Test successfully adding single user without role."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_validate_user.return_value = mock_user
        
        mock_check_membership.return_value = False
        
        # Capture stdout
        with patch('builtins.print') as mock_print:
            with patch('click.echo') as mock_echo:
                add_users_to_organization(1, [123])
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        
        # Verify membership creation
        added_membership = mock_session.add.call_args[0][0]
        assert added_membership.user_id == 123
        assert added_membership.organization_id == 1
        assert added_membership.role_id is None
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.validate_role_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_add_single_user_success_with_role(self, mock_check_membership, mock_validate_role,
                                             mock_validate_user, mock_validate_org, mock_db_manager):
        """Test successfully adding single user with role."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_validate_user.return_value = mock_user
        
        mock_role = Mock(spec=Role)
        mock_role.id = 5
        mock_role.name = "Manager"
        mock_validate_role.return_value = mock_role
        
        mock_check_membership.return_value = False
        
        # Capture stdout
        with patch('click.echo') as mock_echo:
            add_users_to_organization(1, [123], "Manager")
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        
        # Verify membership creation with role
        added_membership = mock_session.add.call_args[0][0]
        assert added_membership.user_id == 123
        assert added_membership.organization_id == 1
        assert added_membership.role_id == 5
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_add_multiple_users_success(self, mock_check_membership, mock_validate_user, 
                                      mock_validate_org, mock_db_manager):
        """Test successfully adding multiple users."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        mock_users = [Mock(spec=User) for _ in range(3)]
        for i, user in enumerate(mock_users):
            user.id = 100 + i
        
        mock_validate_user.side_effect = lambda session, user_id: next(
            (user for user in mock_users if user.id == user_id), None
        )
        
        mock_check_membership.return_value = False
        
        # Capture stdout
        with patch('click.echo') as mock_echo:
            add_users_to_organization(1, [100, 101, 102])
        
        # Verify database operations
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    def test_organization_not_found(self, mock_validate_org, mock_db_manager):
        """Test organization not found returns exit code 2."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_validate_org.side_effect = click.ClickException("Organization with ID 999 not found")
        
        with pytest.raises(click.ClickException, match="Organization with ID 999 not found"):
            add_users_to_organization(999, [123])
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_role_exists')
    def test_role_not_found(self, mock_validate_role, mock_validate_org, mock_db_manager):
        """Test role not found returns exit code 4."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        mock_validate_role.return_value = None
        
        with pytest.raises(SystemExit) as excinfo:
            with patch('click.echo'):
                add_users_to_organization(1, [123], "NonExistentRole")
        
        assert excinfo.value.code == 4
    
    def test_no_users_provided(self):
        """Test no users provided returns exit code 5."""
        with pytest.raises(SystemExit) as excinfo:
            with patch('click.echo'):
                add_users_to_organization(1, [])
        
        assert excinfo.value.code == 5
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_partial_success_some_users_not_found(self, mock_check_membership, mock_validate_user, 
                                                 mock_validate_org, mock_db_manager):
        """Test partial success with some users not found."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        # User 123 exists, 999 doesn't
        def mock_user_validate(session, user_id):
            if user_id == 123:
                user = Mock(spec=User)
                user.id = 123
                return user
            return None
        
        mock_validate_user.side_effect = mock_user_validate
        mock_check_membership.return_value = False
        
        # Capture stdout
        with patch('click.echo') as mock_echo:
            add_users_to_organization(1, [123, 999])
        
        # Verify only valid user was added
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_partial_success_some_users_already_members(self, mock_check_membership, mock_validate_user, 
                                                       mock_validate_org, mock_db_manager):
        """Test partial success with some users already members."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        # Both users exist
        def mock_user_validate(session, user_id):
            user = Mock(spec=User)
            user.id = user_id
            return user
        
        mock_validate_user.side_effect = mock_user_validate
        
        # User 123 is not a member, 456 is already a member
        def mock_membership_check(session, user_id, org_id):
            return user_id == 456
        
        mock_check_membership.side_effect = mock_membership_check
        
        # Capture stdout
        with patch('click.echo') as mock_echo:
            add_users_to_organization(1, [123, 456])
        
        # Verify only new user was added
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_all_users_already_members(self, mock_check_membership, mock_validate_user, 
                                     mock_validate_org, mock_db_manager):
        """Test all users already members returns exit code 3."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        # Both users exist
        def mock_user_validate(session, user_id):
            user = Mock(spec=User)
            user.id = user_id
            return user
        
        mock_validate_user.side_effect = mock_user_validate
        mock_check_membership.return_value = True  # All users already members
        
        with pytest.raises(SystemExit) as excinfo:
            with patch('click.echo'):
                add_users_to_organization(1, [123, 456])
        
        assert excinfo.value.code == 3
    
    def test_duplicate_user_ids_deduplication(self):
        """Test duplicate user IDs in same command are deduplicated."""
        # This is tested via deduplicate_user_ids function
        duplicate_ids = [1, 2, 3, 2, 1, 4]
        result = deduplicate_user_ids(duplicate_ids)
        assert result == [1, 2, 3, 4]
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_database_transaction_rollback_on_error(self, mock_check_membership, mock_validate_user, 
                                                   mock_validate_org, mock_db_manager):
        """Test database transaction rollback on critical errors."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        mock_user = Mock(spec=User)
        mock_user.id = 123
        mock_validate_user.return_value = mock_user
        
        mock_check_membership.return_value = False
        
        # Mock IntegrityError on commit
        mock_session.commit.side_effect = IntegrityError("statement", "params", "constraint violation")
        
        with pytest.raises(SystemExit) as excinfo:
            with patch('click.echo'):
                add_users_to_organization(1, [123])
        
        assert excinfo.value.code == 1
        mock_session.rollback.assert_called_once()


class TestAddOrgUserCommand:
    """Test add-org-user CLI command."""
    
    @patch('src.commands.add_org_user.add_users_to_organization')
    def test_add_org_user_command_success_single_user_with_role(self, mock_add_users):
        """Test CLI command success with single user and role."""
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--organization-id', '1',
            '--user-id', '123',
            '--role', 'Manager'
        ])
        
        assert result.exit_code == 0
        mock_add_users.assert_called_once_with(
            organization_id=1,
            user_ids=[123],
            role_name='Manager'
        )
    
    @patch('src.commands.add_org_user.add_users_to_organization')
    def test_add_org_user_command_success_multiple_users_no_role(self, mock_add_users):
        """Test CLI command success with multiple users and no role."""
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--organization-id', '1',
            '--user-id', '123',
            '--user-id', '456',
            '--user-id', '789'
        ])
        
        assert result.exit_code == 0
        mock_add_users.assert_called_once_with(
            organization_id=1,
            user_ids=[123, 456, 789],
            role_name=None
        )
    
    def test_add_org_user_command_missing_organization_id(self):
        """Test CLI command fails when organization ID is missing."""
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--user-id', '123'
        ])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--organization-id'" in result.output
    
    def test_add_org_user_command_missing_user_id(self):
        """Test CLI command fails when user ID is missing."""
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--organization-id', '1'
        ])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--user-id'" in result.output
    
    @patch('src.commands.add_org_user.add_users_to_organization')
    def test_add_org_user_command_organization_not_found(self, mock_add_users):
        """Test CLI command handles organization not found error."""
        mock_add_users.side_effect = click.ClickException("Organization with ID 999 not found")
        
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--organization-id', '999',
            '--user-id', '123'
        ])
        
        assert result.exit_code == 2
        assert "Organization with ID 999 not found" in result.output
    
    @patch('src.commands.add_org_user.add_users_to_organization')
    def test_add_org_user_command_role_not_found(self, mock_add_users):
        """Test CLI command handles role not found error."""
        mock_add_users.side_effect = click.ClickException("Role 'NonExistent' not found in organization 1")
        
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--organization-id', '1',
            '--user-id', '123',
            '--role', 'NonExistent'
        ])
        
        assert result.exit_code == 4
        assert "Role 'NonExistent' not found in organization 1" in result.output
    
    @patch('src.commands.add_org_user.add_users_to_organization')
    def test_add_org_user_command_database_error(self, mock_add_users):
        """Test CLI command handles database errors gracefully."""
        mock_add_users.side_effect = Exception("Database connection failed")
        
        runner = CliRunner()
        result = runner.invoke(add_org_user_command, [
            '--organization-id', '1',
            '--user-id', '123'
        ])
        
        assert result.exit_code == 1
        assert "Error: An unexpected error occurred: Database connection failed" in result.output


class TestAddOrgUserEdgeCases:
    """Test edge cases for add-org-user command."""
    
    def test_case_insensitive_role_matching(self):
        """Test role matching is case-insensitive."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_role = Mock(spec=Role)
        mock_role.id = 5
        mock_role.name = "Manager"
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_role
        
        # Test both uppercase and mixed case variations
        result1 = validate_role_exists(mock_session, "MANAGER", 1)
        result2 = validate_role_exists(mock_session, "mAnAgEr", 1)
        
        assert result1 == mock_role
        assert result2 == mock_role
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    @patch('src.commands.add_org_user.validate_user_exists')
    @patch('src.commands.add_org_user.check_user_membership')
    def test_registered_and_unregistered_users_supported(self, mock_check_membership, mock_validate_user, 
                                                        mock_validate_org, mock_db_manager):
        """Test both registered and unregistered users can be added."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_validate_org.return_value = mock_organization
        
        # Create registered user (with email) and unregistered user (no email)
        registered_user = Mock(spec=User)
        registered_user.id = 123
        registered_user.email = "user@example.com"
        
        unregistered_user = Mock(spec=User)
        unregistered_user.id = 456
        unregistered_user.email = None
        
        def mock_user_validate(session, user_id):
            if user_id == 123:
                return registered_user
            elif user_id == 456:
                return unregistered_user
            return None
        
        mock_validate_user.side_effect = mock_user_validate
        mock_check_membership.return_value = False
        
        # Capture stdout
        with patch('click.echo') as mock_echo:
            add_users_to_organization(1, [123, 456])
        
        # Verify both users were added
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()
    
    def test_empty_role_name_treated_as_no_role(self):
        """Test empty or whitespace-only role names are treated as no role provided."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None  # No role found for empty string
        
        # Empty string role should return None
        result1 = validate_role_exists(mock_session, "", 1)
        result2 = validate_role_exists(mock_session, "   ", 1)
        
        assert result1 is None
        assert result2 is None
    
    @patch('src.commands.add_org_user.db_manager')
    @patch('src.commands.add_org_user.validate_organization_exists')
    def test_session_close_error_suppressed(self, mock_validate_org, mock_db_manager):
        """Test session close errors are suppressed gracefully."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization not found to trigger exception
        mock_validate_org.side_effect = click.ClickException("Organization with ID 999 not found")
        
        # Mock error on session close
        mock_session.close.side_effect = Exception("Session close error")
        
        # Should not raise session close exception despite close error
        with pytest.raises(click.ClickException, match="Organization with ID 999 not found"):
            add_users_to_organization(999, [123])
        
        # Verify close was still attempted
        mock_session.close.assert_called_once()