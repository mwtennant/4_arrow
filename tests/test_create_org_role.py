"""Tests for create organization role command."""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError

from src.commands.create_org_role import (
    create_org_role,
    validate_role_name,
    parse_permissions_list,
    check_organization_exists,
    check_role_exists_in_org,
    validate_permissions_exist_in_org,
    create_org_role_command
)
from core.models import Organization, Role, Permission, RolePermission
import click
from click.testing import CliRunner


class TestValidateRoleName:
    """Test role name validation."""
    
    def test_validate_valid_name(self):
        """Test validation with valid role name."""
        result = validate_role_name("Tournament Director")
        assert result == "Tournament Director"
    
    def test_validate_name_with_whitespace(self):
        """Test validation trims whitespace."""
        result = validate_role_name("  Score Keeper  ")
        assert result == "Score Keeper"
    
    def test_validate_empty_name_raises_exception(self):
        """Test empty name raises ClickException."""
        with pytest.raises(click.ClickException, match="Role name cannot be empty"):
            validate_role_name("")
    
    def test_validate_whitespace_only_name_raises_exception(self):
        """Test whitespace-only name raises ClickException."""
        with pytest.raises(click.ClickException, match="Role name cannot be empty"):
            validate_role_name("   ")
    
    def test_validate_none_name_raises_exception(self):
        """Test None name raises ClickException."""
        with pytest.raises(click.ClickException, match="Role name cannot be empty"):
            validate_role_name(None)
    
    def test_validate_long_name_raises_exception(self):
        """Test very long name raises ClickException."""
        long_name = "A" * 65  # Over 64 character limit
        with pytest.raises(click.ClickException, match="Role name cannot exceed 64 characters"):
            validate_role_name(long_name)
    
    def test_validate_max_length_name_succeeds(self):
        """Test name at max length succeeds."""
        max_name = "A" * 64  # Exactly 64 characters
        result = validate_role_name(max_name)
        assert result == max_name


class TestParsePermissionsList:
    """Test permissions list parsing."""
    
    def test_parse_valid_permissions_list(self):
        """Test parsing valid comma-separated permissions."""
        result = parse_permissions_list("Create Tournament,Edit Scores,View Reports")
        assert result == ["Create Tournament", "Edit Scores", "View Reports"]
    
    def test_parse_permissions_with_whitespace(self):
        """Test parsing trims whitespace around permissions."""
        result = parse_permissions_list("  Create Tournament  ,  Edit Scores  ,  View Reports  ")
        assert result == ["Create Tournament", "Edit Scores", "View Reports"]
    
    def test_parse_single_permission(self):
        """Test parsing single permission."""
        result = parse_permissions_list("Create Tournament")
        assert result == ["Create Tournament"]
    
    def test_parse_empty_string_returns_empty_list(self):
        """Test empty string returns empty list."""
        result = parse_permissions_list("")
        assert result == []
    
    def test_parse_whitespace_only_returns_empty_list(self):
        """Test whitespace-only string returns empty list."""
        result = parse_permissions_list("   ")
        assert result == []
    
    def test_parse_none_returns_empty_list(self):
        """Test None returns empty list."""
        result = parse_permissions_list(None)
        assert result == []
    
    def test_parse_permissions_with_empty_entries(self):
        """Test parsing filters out empty entries."""
        result = parse_permissions_list("Create Tournament,,Edit Scores,")
        assert result == ["Create Tournament", "Edit Scores"]
    
    def test_parse_permissions_mixed_whitespace(self):
        """Test parsing handles mixed whitespace scenarios."""
        result = parse_permissions_list("Create Tournament, , Edit Scores,  ,View Reports")
        assert result == ["Create Tournament", "Edit Scores", "View Reports"]


class TestCheckOrganizationExists:
    """Test organization existence checking."""
    
    def test_check_organization_exists_true(self):
        """Test returns True when organization exists."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_organization
        
        result = check_organization_exists(mock_session, 1)
        
        assert result is True
        mock_session.query.assert_called_once_with(Organization)
    
    def test_check_organization_exists_false(self):
        """Test returns False when organization doesn't exist."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = check_organization_exists(mock_session, 999)
        
        assert result is False
        mock_session.query.assert_called_once_with(Organization)


class TestCheckRoleExistsInOrg:
    """Test role existence checking within organization."""
    
    def test_check_role_exists_in_org_true(self):
        """Test returns True when role exists in organization."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_role = Mock(spec=Role)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_role
        
        result = check_role_exists_in_org(mock_session, "Tournament Director", 1)
        
        assert result is True
        mock_session.query.assert_called_once_with(Role)
    
    def test_check_role_exists_in_org_false(self):
        """Test returns False when role doesn't exist in organization."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = check_role_exists_in_org(mock_session, "NonExistent Role", 1)
        
        assert result is False
        mock_session.query.assert_called_once_with(Role)


class TestValidatePermissionsExistInOrg:
    """Test permission validation within organization."""
    
    def test_validate_permissions_exist_empty_list(self):
        """Test validation with empty permission list."""
        mock_session = Mock()
        result = validate_permissions_exist_in_org(mock_session, [], 1)
        assert result == []
    
    def test_validate_permissions_exist_single_permission(self):
        """Test validation with single existing permission."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_permission = Mock(spec=Permission)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_permission
        
        result = validate_permissions_exist_in_org(mock_session, ["Create Tournament"], 1)
        
        assert result == [mock_permission]
        mock_session.query.assert_called_once_with(Permission)
    
    def test_validate_permissions_exist_multiple_permissions(self):
        """Test validation with multiple existing permissions."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_perm1 = Mock(spec=Permission)
        mock_perm2 = Mock(spec=Permission)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [mock_perm1, mock_perm2]
        
        result = validate_permissions_exist_in_org(
            mock_session, ["Create Tournament", "Edit Scores"], 1
        )
        
        assert result == [mock_perm1, mock_perm2]
        assert mock_session.query.call_count == 2
    
    def test_validate_permissions_exist_permission_not_found_raises_exception(self):
        """Test validation raises exception when permission doesn't exist."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        with pytest.raises(click.ClickException, match="Permission 'NonExistent' not found in organization"):
            validate_permissions_exist_in_org(mock_session, ["NonExistent"], 1)
    
    def test_validate_permissions_exist_partial_failure_raises_exception(self):
        """Test validation raises exception on first missing permission."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_permission = Mock(spec=Permission)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [mock_permission, None]
        
        with pytest.raises(click.ClickException, match="Permission 'Missing' not found in organization"):
            validate_permissions_exist_in_org(
                mock_session, ["Existing", "Missing"], 1
            )


class TestCreateOrgRole:
    """Test organization role creation."""
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_success_minimal(self, mock_db_manager):
        """Test successful role creation with minimal data."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        result = create_org_role(1, "Tournament Director")
        
        # Verify role was created
        assert isinstance(result, Role)
        assert result.name == "Tournament Director"
        assert result.organization_id == 1
        
        # Verify database operations
        mock_session.add.assert_called_once()
        assert mock_session.commit.call_count == 1  # Only one commit for role creation
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_success_with_permissions(self, mock_db_manager):
        """Test successful role creation with permissions."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        # Mock permissions exist
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        mock_perm1 = Mock(spec=Permission)
        mock_perm1.id = 1
        mock_perm2 = Mock(spec=Permission)
        mock_perm2.id = 2
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.side_effect = [mock_perm1, mock_perm2]
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock role ID after creation
        def add_side_effect(obj):
            if isinstance(obj, Role):
                obj.id = 10
        
        mock_session.add.side_effect = add_side_effect
        
        result = create_org_role(1, "Score Keeper", "Create Tournament,Edit Scores")
        
        # Verify role was created
        assert isinstance(result, Role)
        assert result.name == "Score Keeper"
        assert result.organization_id == 1
        
        # Verify database operations - role + 2 permissions
        assert mock_session.add.call_count == 3  # 1 role + 2 role_permissions
        assert mock_session.commit.call_count == 2  # 1 for role, 1 for permissions
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_trims_whitespace(self, mock_db_manager):
        """Test role creation trims whitespace from fields."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        result = create_org_role(1, "  Tournament Director  ")
        
        # Verify whitespace was trimmed
        assert result.name == "Tournament Director"
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_organization_not_found_raises_exception(self, mock_db_manager):
        """Test organization not found raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        with pytest.raises(click.ClickException, match="Organization not found"):
            create_org_role(999, "Test Role")
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_duplicate_name_raises_exception(self, mock_db_manager):
        """Test duplicate role name raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role exists
        mock_role_query = Mock()
        mock_role_filter = Mock()
        mock_existing_role = Mock(spec=Role)
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = mock_existing_role
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        with pytest.raises(click.ClickException, match="Role with this name already exists in the organization"):
            create_org_role(1, "Existing Role")
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_permission_not_found_raises_exception(self, mock_db_manager):
        """Test missing permission raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        # Mock permission doesn't exist
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.return_value = None
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        with pytest.raises(click.ClickException, match="Permission 'NonExistent' not found in organization"):
            create_org_role(1, "Test Role", "NonExistent")
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_duplicate_name_via_integrity_error_raises_exception(self, mock_db_manager):
        """Test duplicate role name via IntegrityError raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist initially
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock IntegrityError on commit with unique constraint message
        mock_session.commit.side_effect = IntegrityError("statement", "params", "UNIQUE constraint failed: roles.name_organization_id")
        
        with pytest.raises(click.ClickException, match="Role with this name already exists in the organization"):
            create_org_role(1, "Test Role")
        
        # Verify rollback and close
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_create_org_role_invalid_name_raises_exception(self):
        """Test invalid role name raises ClickException."""
        with pytest.raises(click.ClickException, match="Role name cannot be empty"):
            create_org_role(1, "")
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_database_error_raises_exception(self, mock_db_manager):
        """Test general database error raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist initially
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock general exception on commit
        mock_session.commit.side_effect = Exception("Database connection lost")
        
        with pytest.raises(Exception, match="Database connection lost"):
            create_org_role(1, "Test Role")
        
        # Verify rollback and close
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestCreateOrgRoleCommand:
    """Test create-org-role CLI command."""
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_success_minimal(self, mock_create_role):
        """Test CLI command success with minimal arguments."""
        mock_role = Mock(spec=Role)
        mock_role.id = 1
        mock_role.name = "Tournament Director"
        mock_role.organization_id = 1
        mock_create_role.return_value = mock_role
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', 'Tournament Director'
        ])
        
        assert result.exit_code == 0
        assert "Role created successfully!" in result.output
        assert "Role ID: 1" in result.output
        assert "Name: Tournament Director" in result.output
        assert "Organization ID: 1" in result.output
        
        mock_create_role.assert_called_once_with(
            organization_id=1,
            name='Tournament Director',
            permissions=None
        )
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_success_with_permissions(self, mock_create_role):
        """Test CLI command success with permissions."""
        mock_role = Mock(spec=Role)
        mock_role.id = 2
        mock_role.name = "Score Keeper"
        mock_role.organization_id = 1
        mock_create_role.return_value = mock_role
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', 'Score Keeper',
            '--permissions', 'Create Tournament,Edit Scores'
        ])
        
        assert result.exit_code == 0
        assert "Role created successfully!" in result.output
        assert "Role ID: 2" in result.output
        assert "Name: Score Keeper" in result.output
        assert "Organization ID: 1" in result.output
        assert "Assigned permissions: Create Tournament, Edit Scores" in result.output
        
        mock_create_role.assert_called_once_with(
            organization_id=1,
            name='Score Keeper',
            permissions='Create Tournament,Edit Scores'
        )
    
    def test_create_org_role_command_missing_organization_id_fails(self):
        """Test CLI command fails when organization-id is missing."""
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--name', 'Test Role'
        ])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--organization-id'" in result.output
    
    def test_create_org_role_command_missing_name_fails(self):
        """Test CLI command fails when name is missing."""
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1'
        ])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--name'" in result.output
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_organization_not_found_fails(self, mock_create_role):
        """Test CLI command fails with exit code 2 when organization not found."""
        mock_create_role.side_effect = click.ClickException("Organization not found")
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '999',
            '--name', 'Test Role'
        ])
        
        assert result.exit_code == 2  # Organization not found exit code
        assert "Organization not found" in result.output
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_duplicate_role_fails(self, mock_create_role):
        """Test CLI command fails with exit code 3 when role exists."""
        mock_create_role.side_effect = click.ClickException("Role with this name already exists in the organization")
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', 'Existing Role'
        ])
        
        assert result.exit_code == 3  # Duplicate role exit code
        assert "Role with this name already exists in the organization" in result.output
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_permission_not_found_fails(self, mock_create_role):
        """Test CLI command fails with exit code 4 when permission not found."""
        mock_create_role.side_effect = click.ClickException("Permission 'NonExistent' not found in organization")
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', 'Test Role',
            '--permissions', 'NonExistent'
        ])
        
        assert result.exit_code == 4  # Permission not found exit code
        assert "Permission 'NonExistent' not found in organization" in result.output
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_empty_name_fails(self, mock_create_role):
        """Test CLI command fails when name is empty."""
        mock_create_role.side_effect = click.ClickException("Role name cannot be empty")
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', ''
        ])
        
        assert result.exit_code == 1
        assert "Role name cannot be empty" in result.output
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_database_error_fails(self, mock_create_role):
        """Test CLI command handles database errors gracefully."""
        mock_create_role.side_effect = Exception("Database connection failed")
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', 'Test Role'
        ])
        
        assert result.exit_code == 1
        assert "Error: Database connection failed" in result.output


class TestCreateOrgRoleEdgeCases:
    """Test edge cases for organization role creation."""
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_case_insensitive_duplicate_check(self, mock_db_manager):
        """Test duplicate check is case-insensitive."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role exists (case insensitive)
        mock_role_query = Mock()
        mock_role_filter = Mock()
        mock_existing_role = Mock(spec=Role)
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = mock_existing_role
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        with pytest.raises(click.ClickException, match="Role with this name already exists in the organization"):
            create_org_role(1, "tournament director")  # Different case
        
        # Verify database operations
        mock_session.close.assert_called_once()
    
    def test_validate_role_name_unicode_characters(self):
        """Test validation handles unicode characters."""
        unicode_name = "Directeur de Tournoi"
        result = validate_role_name(unicode_name)
        assert result == unicode_name
    
    def test_validate_role_name_special_characters(self):
        """Test validation handles special characters."""
        special_name = "Tournament Director & Score Keeper (Admin)"
        result = validate_role_name(special_name)
        assert result == special_name
    
    @patch('src.commands.create_org_role.db_manager')
    def test_create_org_role_handles_session_close_error(self, mock_db_manager):
        """Test role creation handles session close errors gracefully."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock role doesn't exist
        mock_role_query = Mock()
        mock_role_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Role:
                mock_role_query.filter.return_value = mock_role_filter
                mock_role_filter.first.return_value = None
                return mock_role_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock error on session close
        mock_session.close.side_effect = Exception("Session close error")
        
        # Should still succeed despite close error
        result = create_org_role(1, "Test Role")
        
        assert isinstance(result, Role)
        assert result.name == "Test Role"
        
        # Verify database operations still occurred
        mock_session.add.assert_called_once()
        assert mock_session.commit.call_count == 1
        mock_session.close.assert_called_once()
    
    def test_parse_permissions_list_case_sensitivity(self):
        """Test permissions parsing preserves case."""
        result = parse_permissions_list("Create Tournament,EDIT SCORES,view reports")
        assert result == ["Create Tournament", "EDIT SCORES", "view reports"]
    
    @patch('src.commands.create_org_role.create_org_role')
    def test_create_org_role_command_empty_permissions_list_not_shown(self, mock_create_role):
        """Test CLI command doesn't show empty permissions."""
        mock_role = Mock(spec=Role)
        mock_role.id = 1
        mock_role.name = "Test Role"
        mock_role.organization_id = 1
        mock_create_role.return_value = mock_role
        
        runner = CliRunner()
        result = runner.invoke(create_org_role_command, [
            '--organization-id', '1',
            '--name', 'Test Role',
            '--permissions', ''
        ])
        
        assert result.exit_code == 0
        assert "Assigned permissions:" not in result.output
        
        mock_create_role.assert_called_once_with(
            organization_id=1,
            name='Test Role',
            permissions=''
        )