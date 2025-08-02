"""Tests for create organization permission command."""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError

from src.commands.create_org_permission import (
    create_org_permission,
    validate_permission_name,
    validate_permission_description,
    check_organization_exists,
    check_permission_exists_in_org,
    create_org_permission_command
)
from core.models import Organization, Permission
import click
from click.testing import CliRunner


class TestValidatePermissionName:
    """Test permission name validation."""
    
    def test_validate_valid_name(self):
        """Test validation with valid permission name."""
        result = validate_permission_name("Create Tournament")
        assert result == "Create Tournament"
    
    def test_validate_name_with_whitespace(self):
        """Test validation trims whitespace."""
        result = validate_permission_name("  Edit Scores  ")
        assert result == "Edit Scores"
    
    def test_validate_empty_name_raises_exception(self):
        """Test empty name raises ClickException."""
        with pytest.raises(click.ClickException, match="Permission name cannot be empty"):
            validate_permission_name("")
    
    def test_validate_whitespace_only_name_raises_exception(self):
        """Test whitespace-only name raises ClickException."""
        with pytest.raises(click.ClickException, match="Permission name cannot be empty"):
            validate_permission_name("   ")
    
    def test_validate_none_name_raises_exception(self):
        """Test None name raises ClickException."""
        with pytest.raises(click.ClickException, match="Permission name cannot be empty"):
            validate_permission_name(None)
    
    def test_validate_long_name_raises_exception(self):
        """Test very long name raises ClickException."""
        long_name = "A" * 65  # Over 64 character limit
        with pytest.raises(click.ClickException, match="Permission name cannot exceed 64 characters"):
            validate_permission_name(long_name)
    
    def test_validate_max_length_name_succeeds(self):
        """Test name at max length succeeds."""
        max_name = "A" * 64  # Exactly 64 characters
        result = validate_permission_name(max_name)
        assert result == max_name


class TestValidatePermissionDescription:
    """Test permission description validation."""
    
    def test_validate_valid_description(self):
        """Test validation with valid description."""
        result = validate_permission_description("Allow creating new tournaments")
        assert result == "Allow creating new tournaments"
    
    def test_validate_description_with_whitespace(self):
        """Test validation trims whitespace."""
        result = validate_permission_description("  Allow editing scores  ")
        assert result == "Allow editing scores"
    
    def test_validate_empty_description_returns_empty_string(self):
        """Test empty description returns empty string."""
        result = validate_permission_description("")
        assert result == ""
    
    def test_validate_none_description_returns_none(self):
        """Test None description returns None."""
        result = validate_permission_description(None)
        assert result is None
    
    def test_validate_long_description_raises_exception(self):
        """Test very long description raises ClickException."""
        long_description = "A" * 256  # Over 255 character limit
        with pytest.raises(click.ClickException, match="Permission description cannot exceed 255 characters"):
            validate_permission_description(long_description)
    
    def test_validate_max_length_description_succeeds(self):
        """Test description at max length succeeds."""
        max_description = "A" * 255  # Exactly 255 characters
        result = validate_permission_description(max_description)
        assert result == max_description


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


class TestCheckPermissionExistsInOrg:
    """Test permission existence checking within organization."""
    
    def test_check_permission_exists_in_org_true(self):
        """Test returns True when permission exists in organization."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_permission = Mock(spec=Permission)
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_permission
        
        result = check_permission_exists_in_org(mock_session, "Create Tournament", 1)
        
        assert result is True
        mock_session.query.assert_called_once_with(Permission)
    
    def test_check_permission_exists_in_org_false(self):
        """Test returns False when permission doesn't exist in organization."""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = check_permission_exists_in_org(mock_session, "NonExistent Permission", 1)
        
        assert result is False
        mock_session.query.assert_called_once_with(Permission)


class TestCreateOrgPermission:
    """Test organization permission creation."""
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_success_minimal(self, mock_db_manager):
        """Test successful permission creation with minimal data."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        mock_session.query.return_value = mock_org_query
        mock_org_query.filter.return_value = mock_org_filter
        mock_org_filter.first.return_value = mock_organization
        
        # Mock permission doesn't exist
        def query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Permission:
                perm_query = Mock()
                perm_filter = Mock()
                perm_filter.first.return_value = None
                perm_query.filter.return_value = perm_filter
                return perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        result = create_org_permission(1, "Create Tournament")
        
        # Verify permission was created
        assert isinstance(result, Permission)
        assert result.name == "Create Tournament"
        assert result.organization_id == 1
        assert result.description is None
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_success_with_description(self, mock_db_manager):
        """Test successful permission creation with description."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        mock_session.query.return_value = mock_org_query
        mock_org_query.filter.return_value = mock_org_filter
        mock_org_filter.first.return_value = mock_organization
        
        # Mock permission doesn't exist
        def query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Permission:
                perm_query = Mock()
                perm_filter = Mock()
                perm_filter.first.return_value = None
                perm_query.filter.return_value = perm_filter
                return perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        result = create_org_permission(1, "Edit Scores", "Allow editing tournament scores")
        
        # Verify permission was created with description
        assert isinstance(result, Permission)
        assert result.name == "Edit Scores"
        assert result.organization_id == 1
        assert result.description == "Allow editing tournament scores"
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_trims_whitespace(self, mock_db_manager):
        """Test permission creation trims whitespace from fields."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        mock_session.query.return_value = mock_org_query
        mock_org_query.filter.return_value = mock_org_filter
        mock_org_filter.first.return_value = mock_organization
        
        # Mock permission doesn't exist
        def query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Permission:
                perm_query = Mock()
                perm_filter = Mock()
                perm_filter.first.return_value = None
                perm_query.filter.return_value = perm_filter
                return perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        result = create_org_permission(1, "  Create Tournament  ", "  Allow creating tournaments  ")
        
        # Verify whitespace was trimmed
        assert result.name == "Create Tournament"
        assert result.description == "Allow creating tournaments"
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_handles_empty_description(self, mock_db_manager):
        """Test permission creation handles empty description."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        mock_session.query.return_value = mock_org_query
        mock_org_query.filter.return_value = mock_org_filter
        mock_org_filter.first.return_value = mock_organization
        
        # Mock permission doesn't exist
        def query_side_effect(model):
            if model == Organization:
                return mock_org_query
            elif model == Permission:
                perm_query = Mock()
                perm_filter = Mock()
                perm_filter.first.return_value = None
                perm_query.filter.return_value = perm_filter
                return perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        result = create_org_permission(1, "Test Permission", "")
        
        # Verify empty description becomes empty string
        assert result.name == "Test Permission"
        assert result.description == ""
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_organization_not_found_raises_exception(self, mock_db_manager):
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
            create_org_permission(999, "Test Permission")
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_duplicate_name_raises_exception(self, mock_db_manager):
        """Test duplicate permission name raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock permission exists
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        mock_existing_permission = Mock(spec=Permission)
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.return_value = mock_existing_permission
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        with pytest.raises(click.ClickException, match="Permission with this name already exists in the organization"):
            create_org_permission(1, "Existing Permission")
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_duplicate_name_via_integrity_error_raises_exception(self, mock_db_manager):
        """Test duplicate permission name via IntegrityError raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock permission doesn't exist initially
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.return_value = None
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock IntegrityError on commit with unique constraint message
        mock_session.commit.side_effect = IntegrityError("statement", "params", "UNIQUE constraint failed: permissions.name_organization_id")
        
        with pytest.raises(click.ClickException, match="Permission with this name already exists in the organization"):
            create_org_permission(1, "Test Permission")
        
        # Verify rollback and close
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_create_org_permission_invalid_name_raises_exception(self):
        """Test invalid permission name raises ClickException."""
        with pytest.raises(click.ClickException, match="Permission name cannot be empty"):
            create_org_permission(1, "")
    
    def test_create_org_permission_invalid_description_raises_exception(self):
        """Test invalid permission description raises ClickException."""
        long_description = "A" * 256  # Over limit
        with pytest.raises(click.ClickException, match="Permission description cannot exceed 255 characters"):
            create_org_permission(1, "Test Permission", long_description)
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_database_error_raises_exception(self, mock_db_manager):
        """Test general database error raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock permission doesn't exist initially
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.return_value = None
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock general exception on commit
        mock_session.commit.side_effect = Exception("Database connection lost")
        
        with pytest.raises(Exception, match="Database connection lost"):
            create_org_permission(1, "Test Permission")
        
        # Verify rollback and close
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestCreateOrgPermissionCommand:
    """Test create-org-permission CLI command."""
    
    @patch('src.commands.create_org_permission.create_org_permission')
    def test_create_org_permission_command_success_minimal(self, mock_create_perm):
        """Test CLI command success with minimal arguments."""
        mock_permission = Mock(spec=Permission)
        mock_permission.id = 1
        mock_permission.name = "Create Tournament"
        mock_permission.organization_id = 1
        mock_permission.description = None
        mock_create_perm.return_value = mock_permission
        
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '1',
            '--name', 'Create Tournament'
        ])
        
        assert result.exit_code == 0
        assert "Permission created successfully!" in result.output
        assert "Permission ID: 1" in result.output
        assert "Name: Create Tournament" in result.output
        assert "Organization ID: 1" in result.output
        
        mock_create_perm.assert_called_once_with(
            organization_id=1,
            name='Create Tournament',
            description=None
        )
    
    @patch('src.commands.create_org_permission.create_org_permission')
    def test_create_org_permission_command_success_with_description(self, mock_create_perm):
        """Test CLI command success with description."""
        mock_permission = Mock(spec=Permission)
        mock_permission.id = 2
        mock_permission.name = "Edit Scores"
        mock_permission.organization_id = 1
        mock_permission.description = "Allow editing tournament scores"
        mock_create_perm.return_value = mock_permission
        
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '1',
            '--name', 'Edit Scores',
            '--description', 'Allow editing tournament scores'
        ])
        
        assert result.exit_code == 0
        assert "Permission created successfully!" in result.output
        assert "Permission ID: 2" in result.output
        assert "Name: Edit Scores" in result.output
        assert "Organization ID: 1" in result.output
        assert "Description: Allow editing tournament scores" in result.output
        
        mock_create_perm.assert_called_once_with(
            organization_id=1,
            name='Edit Scores',
            description='Allow editing tournament scores'
        )
    
    def test_create_org_permission_command_missing_organization_id_fails(self):
        """Test CLI command fails when organization-id is missing."""
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--name', 'Test Permission'
        ])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--organization-id'" in result.output
    
    def test_create_org_permission_command_missing_name_fails(self):
        """Test CLI command fails when name is missing."""
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '1'
        ])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--name'" in result.output
    
    @patch('src.commands.create_org_permission.create_org_permission')
    def test_create_org_permission_command_organization_not_found_fails(self, mock_create_perm):
        """Test CLI command fails with exit code 2 when organization not found."""
        mock_create_perm.side_effect = click.ClickException("Organization not found")
        
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '999',
            '--name', 'Test Permission'
        ])
        
        assert result.exit_code == 2  # Organization not found exit code
        assert "Organization not found" in result.output
    
    @patch('src.commands.create_org_permission.create_org_permission')
    def test_create_org_permission_command_duplicate_permission_fails(self, mock_create_perm):
        """Test CLI command fails with exit code 3 when permission exists."""
        mock_create_perm.side_effect = click.ClickException("Permission with this name already exists in the organization")
        
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '1',
            '--name', 'Existing Permission'
        ])
        
        assert result.exit_code == 3  # Duplicate permission exit code
        assert "Permission with this name already exists in the organization" in result.output
    
    @patch('src.commands.create_org_permission.create_org_permission')
    def test_create_org_permission_command_empty_name_fails(self, mock_create_perm):
        """Test CLI command fails when name is empty."""
        mock_create_perm.side_effect = click.ClickException("Permission name cannot be empty")
        
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '1',
            '--name', ''
        ])
        
        assert result.exit_code == 1
        assert "Permission name cannot be empty" in result.output
    
    @patch('src.commands.create_org_permission.create_org_permission')
    def test_create_org_permission_command_database_error_fails(self, mock_create_perm):
        """Test CLI command handles database errors gracefully."""
        mock_create_perm.side_effect = Exception("Database connection failed")
        
        runner = CliRunner()
        result = runner.invoke(create_org_permission_command, [
            '--organization-id', '1',
            '--name', 'Test Permission'
        ])
        
        assert result.exit_code == 1
        assert "Error: Database connection failed" in result.output


class TestCreateOrgPermissionEdgeCases:
    """Test edge cases for organization permission creation."""
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_case_insensitive_duplicate_check(self, mock_db_manager):
        """Test duplicate check is case-insensitive."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock permission exists (case insensitive)
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        mock_existing_permission = Mock(spec=Permission)
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.return_value = mock_existing_permission
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        with pytest.raises(click.ClickException, match="Permission with this name already exists in the organization"):
            create_org_permission(1, "create tournament")  # Different case
        
        # Verify database operations
        mock_session.close.assert_called_once()
    
    def test_validate_permission_name_unicode_characters(self):
        """Test validation handles unicode characters."""
        unicode_name = "Créer Tournoi"
        result = validate_permission_name(unicode_name)
        assert result == unicode_name
    
    def test_validate_permission_name_special_characters(self):
        """Test validation handles special characters."""
        special_name = "Create & Edit Tournament (Admin)"
        result = validate_permission_name(special_name)
        assert result == special_name
    
    @patch('src.commands.create_org_permission.db_manager')
    def test_create_org_permission_handles_session_close_error(self, mock_db_manager):
        """Test permission creation handles session close errors gracefully."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org_query = Mock()
        mock_org_filter = Mock()
        mock_organization = Mock(spec=Organization)
        
        # Mock permission doesn't exist
        mock_perm_query = Mock()
        mock_perm_filter = Mock()
        
        def query_side_effect(model):
            if model == Organization:
                mock_org_query.filter.return_value = mock_org_filter
                mock_org_filter.first.return_value = mock_organization
                return mock_org_query
            elif model == Permission:
                mock_perm_query.filter.return_value = mock_perm_filter
                mock_perm_filter.first.return_value = None
                return mock_perm_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock error on session close
        mock_session.close.side_effect = Exception("Session close error")
        
        # Should still succeed despite close error
        result = create_org_permission(1, "Test Permission")
        
        assert isinstance(result, Permission)
        assert result.name == "Test Permission"
        
        # Verify database operations still occurred
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()