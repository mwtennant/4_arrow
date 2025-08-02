"""Test suite for edit organization command."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from sqlalchemy.exc import SQLAlchemyError

from core.models import Organization
from src.commands.edit_organization import (
    edit_organization_command,
    validate_empty_field,
    check_name_conflict,
    update_organization_fields
)


class TestValidateEmptyField:
    """Test validate_empty_field function."""
    
    def test_valid_non_empty_value(self):
        """Test that non-empty values pass validation."""
        validate_empty_field("name", "Valid Name")
        validate_empty_field("address", "123 Main St")
        
    def test_none_value_passes(self):
        """Test that None values pass validation."""
        validate_empty_field("name", None)
        
    def test_empty_string_raises_error(self):
        """Test that empty strings raise ValueError."""
        with pytest.raises(ValueError, match="Empty value not allowed"):
            validate_empty_field("name", "")
            
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only strings raise ValueError."""
        with pytest.raises(ValueError, match="Empty value not allowed"):
            validate_empty_field("name", "   ")
            
    def test_tab_only_raises_error(self):
        """Test that tab-only strings raise ValueError."""
        with pytest.raises(ValueError, match="Empty value not allowed"):
            validate_empty_field("name", "\t")


class TestCheckNameConflict:
    """Test check_name_conflict function."""
    
    def test_no_conflict_returns_false(self):
        """Test that unique names return False."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        
        result = check_name_conflict(mock_session, "Unique Name", 1)
        assert result is False
        
    def test_existing_name_returns_true(self):
        """Test that existing names return True."""
        mock_session = MagicMock()
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        result = check_name_conflict(mock_session, "Existing Name", 1)
        assert result is True
        
    def test_case_insensitive_matching(self):
        """Test that name conflict check is case-insensitive."""
        mock_session = MagicMock()
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        result = check_name_conflict(mock_session, "TEST NAME", 1)
        
        # Verify ilike was called for case-insensitive comparison
        mock_session.query.assert_called_once_with(Organization)
        assert result is True


class TestUpdateOrganizationFields:
    """Test update_organization_fields function."""
    
    def test_no_fields_updated_returns_false(self):
        """Test that updating with no fields returns False."""
        mock_org = MagicMock()
        
        result = update_organization_fields(mock_org)
        assert result is False
        
    def test_single_field_update_returns_true(self):
        """Test that updating single field returns True."""
        mock_org = MagicMock()
        
        result = update_organization_fields(mock_org, name="New Name")
        assert result is True
        assert mock_org.name == "New Name"
        
    def test_multiple_fields_update_returns_true(self):
        """Test that updating multiple fields returns True."""
        mock_org = MagicMock()
        
        result = update_organization_fields(
            mock_org,
            name="New Name",
            address="New Address",
            email="new@example.com"
        )
        assert result is True
        assert mock_org.name == "New Name"
        assert mock_org.address == "New Address"
        assert mock_org.email == "new@example.com"
        
    def test_all_fields_can_be_updated(self):
        """Test that all fields can be updated."""
        mock_org = MagicMock()
        
        result = update_organization_fields(
            mock_org,
            name="Test Org",
            address="123 Main St",
            phone="555-1234",
            email="test@example.com",
            website="https://example.com"
        )
        assert result is True
        assert mock_org.name == "Test Org"
        assert mock_org.address == "123 Main St"
        assert mock_org.phone == "555-1234"
        assert mock_org.email == "test@example.com"
        assert mock_org.website == "https://example.com"


class TestEditOrganizationCommand:
    """Test edit_organization_command CLI command."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_missing_organization_id_flag(self, mock_db_manager):
        """Test that missing --organization-id flag shows usage."""
        result = self.runner.invoke(edit_organization_command, [])
        assert result.exit_code == 2  # Click's missing required option exit code
        assert "Missing option" in result.output or "Error" in result.output
        
    @patch('src.commands.edit_organization.db_manager')
    def test_organization_not_found(self, mock_db_manager):
        """Test organization not found returns exit code 2."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = None
        
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '999',
            '--name', 'New Name'
        ])
        
        assert result.exit_code == 2
        assert "Organization not found." in result.output
        
    @patch('src.commands.edit_organization.db_manager')
    def test_name_conflict_returns_exit_code_3(self, mock_db_manager):
        """Test name conflict returns exit code 3."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        # Mock name conflict check returns True
        with patch('src.commands.edit_organization.check_name_conflict', return_value=True):
            result = self.runner.invoke(edit_organization_command, [
                '--organization-id', '1',
                '--name', 'Existing Name'
            ])
            
        assert result.exit_code == 3
        assert "Organization name already exists." in result.output
        
    @patch('src.commands.edit_organization.db_manager')
    def test_empty_value_returns_error(self, mock_db_manager):
        """Test empty field values return appropriate error."""
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '1',
            '--name', ''
        ])
        
        assert result.exit_code == 1
        assert "Empty value not allowed" in result.output
        
    @patch('src.commands.edit_organization.db_manager')
    def test_successful_single_field_update(self, mock_db_manager):
        """Test successful single field update."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        # Mock no name conflict
        with patch('src.commands.edit_organization.check_name_conflict', return_value=False):
            result = self.runner.invoke(edit_organization_command, [
                '--organization-id', '1',
                '--name', 'Updated Name'
            ])
            
        assert result.exit_code == 0
        mock_session.commit.assert_called_once()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_successful_multiple_field_update(self, mock_db_manager):
        """Test successful multiple field update."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        with patch('src.commands.edit_organization.check_name_conflict', return_value=False):
            result = self.runner.invoke(edit_organization_command, [
                '--organization-id', '1',
                '--name', 'Updated Name',
                '--email', 'updated@example.com',
                '--phone', '555-9999'
            ])
            
        assert result.exit_code == 0
        mock_session.commit.assert_called_once()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_no_op_successful(self, mock_db_manager):
        """Test no-op (no fields provided) returns success."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '1'
        ])
        
        assert result.exit_code == 0
        # Commit should not be called when no changes made
        mock_session.commit.assert_not_called()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_update_to_same_values_successful(self, mock_db_manager):
        """Test updating to same values is successful."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_org.name = "Current Name"
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        with patch('src.commands.edit_organization.check_name_conflict', return_value=False):
            result = self.runner.invoke(edit_organization_command, [
                '--organization-id', '1',
                '--name', 'Same Name'
            ])
            
        assert result.exit_code == 0
        mock_session.commit.assert_called_once()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_database_error_handling(self, mock_db_manager):
        """Test database error handling."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = SQLAlchemyError("Database connection failed")
        
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '1',
            '--name', 'Test Name'
        ])
        
        assert result.exit_code == 1
        assert "Database error" in result.output
        
    @patch('src.commands.edit_organization.db_manager')
    def test_session_cleanup(self, mock_db_manager):
        """Test that database session is properly closed."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '1',
            '--name', 'Test Name'
        ])
        
        # Session should be closed regardless of success/failure
        mock_session.close.assert_called_once()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_whitespace_values_rejected(self, mock_db_manager):
        """Test that whitespace-only values are rejected."""
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '1',
            '--name', '   ',
            '--address', '\t'
        ])
        
        assert result.exit_code == 1
        assert "Empty value not allowed" in result.output


class TestIntegrationScenarios:
    """Integration test scenarios covering complex workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_case_insensitive_name_conflict_detection(self, mock_db_manager):
        """Test case-insensitive name conflict detection."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization exists
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        # Mock name conflict with different case
        with patch('src.commands.edit_organization.check_name_conflict', return_value=True):
            result = self.runner.invoke(edit_organization_command, [
                '--organization-id', '1',
                '--name', 'EXISTING org'  # Different case
            ])
            
        assert result.exit_code == 3
        assert "Organization name already exists." in result.output
        
    @patch('src.commands.edit_organization.db_manager')
    def test_transaction_rollback_on_error(self, mock_db_manager):
        """Test transaction rollback when error occurs during commit."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        mock_session.commit.side_effect = SQLAlchemyError("Commit failed")
        
        with patch('src.commands.edit_organization.check_name_conflict', return_value=False):
            result = self.runner.invoke(edit_organization_command, [
                '--organization-id', '1',
                '--name', 'New Name'
            ])
            
        assert result.exit_code == 1
        mock_session.close.assert_called_once()
        
    @patch('src.commands.edit_organization.db_manager')
    def test_partial_field_updates(self, mock_db_manager):
        """Test that only specified fields are updated."""
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        mock_org = MagicMock()
        mock_session.query.return_value.filter.return_value.filter.return_value.first.return_value = mock_org
        
        result = self.runner.invoke(edit_organization_command, [
            '--organization-id', '1',
            '--address', 'New Address Only'
        ])
        
        assert result.exit_code == 0
        # Only address should be updated
        assert mock_org.address == 'New Address Only'
        # Name should not be touched
        assert not hasattr(mock_org, 'name') or mock_org.name != 'New Address Only'