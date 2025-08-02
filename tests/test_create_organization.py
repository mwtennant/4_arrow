"""Tests for create organization command."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.exc import IntegrityError

from src.commands.create_organization import (
    create_organization,
    validate_organization_name,
    check_organization_exists,
    create_organization_command
)
from core.models import Organization
import click
from click.testing import CliRunner


class TestValidateOrganizationName:
    """Test organization name validation."""
    
    def test_validate_valid_name(self):
        """Test validation with valid organization name."""
        result = validate_organization_name("4th Arrow Bowling Center")
        assert result == "4th Arrow Bowling Center"
    
    def test_validate_name_with_whitespace(self):
        """Test validation trims whitespace."""
        result = validate_organization_name("  Pine Valley Lanes  ")
        assert result == "Pine Valley Lanes"
    
    def test_validate_empty_name_raises_exception(self):
        """Test empty name raises ClickException."""
        with pytest.raises(click.ClickException, match="Organization name cannot be empty"):
            validate_organization_name("")
    
    def test_validate_whitespace_only_name_raises_exception(self):
        """Test whitespace-only name raises ClickException."""
        with pytest.raises(click.ClickException, match="Organization name cannot be empty"):
            validate_organization_name("   ")
    
    def test_validate_none_name_raises_exception(self):
        """Test None name raises ClickException."""
        with pytest.raises(click.ClickException, match="Organization name cannot be empty"):
            validate_organization_name(None)
    
    def test_validate_long_name_raises_exception(self):
        """Test very long name raises ClickException."""
        long_name = "A" * 256  # Over 255 character limit
        with pytest.raises(click.ClickException, match="Organization name cannot exceed 255 characters"):
            validate_organization_name(long_name)
    
    def test_validate_max_length_name_succeeds(self):
        """Test name at max length succeeds."""
        max_name = "A" * 255  # Exactly 255 characters
        result = validate_organization_name(max_name)
        assert result == max_name


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
        
        result = check_organization_exists(mock_session, "Test Org")
        
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
        
        result = check_organization_exists(mock_session, "NonExistent Org")
        
        assert result is False
        mock_session.query.assert_called_once_with(Organization)


class TestCreateOrganization:
    """Test organization creation."""
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_success_minimal(self, mock_db_manager):
        """Test successful organization creation with minimal data."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = create_organization("Test Organization")
        
        # Verify organization was created
        assert isinstance(result, Organization)
        assert result.name == "Test Organization"
        assert result.address is None
        assert result.phone is None
        assert result.email is None
        assert result.website is None
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_success_full_data(self, mock_db_manager):
        """Test successful organization creation with all data."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = create_organization(
            name="Pine Valley Lanes",
            address="123 Main St",
            phone="555-1234",
            email="info@pinevalley.com",
            website="https://pinevalley.com"
        )
        
        # Verify organization was created with all data
        assert isinstance(result, Organization)
        assert result.name == "Pine Valley Lanes"
        assert result.address == "123 Main St"
        assert result.phone == "555-1234"
        assert result.email == "info@pinevalley.com"
        assert result.website == "https://pinevalley.com"
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_trims_whitespace(self, mock_db_manager):
        """Test organization creation trims whitespace from fields."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = create_organization(
            name="  Test Org  ",
            address="  123 Main St  ",
            phone="  555-1234  ",
            email="  test@example.com  ",
            website="  https://example.com  "
        )
        
        # Verify whitespace was trimmed
        assert result.name == "Test Org"
        assert result.address == "123 Main St"
        assert result.phone == "555-1234"
        assert result.email == "test@example.com"
        assert result.website == "https://example.com"
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_handles_empty_optional_fields(self, mock_db_manager):
        """Test organization creation handles empty optional fields."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = create_organization(
            name="Test Org",
            address="",
            phone="   ",
            email=None,
            website=""
        )
        
        # Verify empty fields are set to None
        assert result.name == "Test Org"
        assert result.address is None  # Empty string becomes None
        assert result.phone is None    # Whitespace-only becomes None
        assert result.email is None
        assert result.website is None
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_duplicate_name_raises_exception(self, mock_db_manager):
        """Test duplicate organization name raises ClickException via IntegrityError."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock IntegrityError with unique constraint message
        mock_session.commit.side_effect = IntegrityError("statement", "params", "UNIQUE constraint failed: organizations.name")
        
        with pytest.raises(click.ClickException, match="Organization with this name already exists"):
            create_organization("Existing Organization")
        
        # Verify session was rolled back and closed
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_create_organization_invalid_name_raises_exception(self):
        """Test invalid organization name raises ClickException."""
        with pytest.raises(click.ClickException, match="Organization name cannot be empty"):
            create_organization("")
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_integrity_error_raises_exception(self, mock_db_manager):
        """Test IntegrityError raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist initially
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        # Mock IntegrityError on commit with unique constraint message
        mock_session.commit.side_effect = IntegrityError("statement", "params", "UNIQUE constraint failed: organizations.name")
        
        with pytest.raises(click.ClickException, match="Organization with this name already exists"):
            create_organization("Test Org")
        
        # Verify rollback and close
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_database_error_raises_exception(self, mock_db_manager):
        """Test general database error raises ClickException."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist initially
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        # Mock general exception on commit
        mock_session.commit.side_effect = Exception("Database connection lost")
        
        with pytest.raises(click.ClickException, match="Database error: Database connection lost"):
            create_organization("Test Org")
        
        # Verify rollback and close
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestCreateOrganizationCommand:
    """Test create-organization CLI command."""
    
    @patch('src.commands.create_organization.create_organization')
    def test_create_organization_command_success_minimal(self, mock_create_org):
        """Test CLI command success with minimal arguments."""
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 1
        mock_organization.name = "Test Organization"
        mock_organization.address = None
        mock_organization.phone = None
        mock_organization.email = None
        mock_organization.website = None
        mock_create_org.return_value = mock_organization
        
        runner = CliRunner()
        result = runner.invoke(create_organization_command, [
            '--name', 'Test Organization'
        ])
        
        assert result.exit_code == 0
        assert "Organization created successfully!" in result.output
        assert "Organization ID: 1" in result.output
        assert "Name: Test Organization" in result.output
        
        mock_create_org.assert_called_once_with(
            name='Test Organization',
            address=None,
            phone=None,
            email=None,
            website=None
        )
    
    @patch('src.commands.create_organization.create_organization')
    def test_create_organization_command_success_full_data(self, mock_create_org):
        """Test CLI command success with all arguments."""
        mock_organization = Mock(spec=Organization)
        mock_organization.id = 2
        mock_organization.name = "Pine Valley Lanes"
        mock_organization.address = "123 Main St"
        mock_organization.phone = "555-1234"
        mock_organization.email = "info@pinevalley.com"
        mock_organization.website = "https://pinevalley.com"
        mock_create_org.return_value = mock_organization
        
        runner = CliRunner()
        result = runner.invoke(create_organization_command, [
            '--name', 'Pine Valley Lanes',
            '--address', '123 Main St',
            '--phone', '555-1234',
            '--email', 'info@pinevalley.com',
            '--website', 'https://pinevalley.com'
        ])
        
        assert result.exit_code == 0
        assert "Organization created successfully!" in result.output
        assert "Organization ID: 2" in result.output
        assert "Name: Pine Valley Lanes" in result.output
        assert "Address: 123 Main St" in result.output
        assert "Phone: 555-1234" in result.output
        assert "Email: info@pinevalley.com" in result.output
        assert "Website: https://pinevalley.com" in result.output
        
        mock_create_org.assert_called_once_with(
            name='Pine Valley Lanes',
            address='123 Main St',
            phone='555-1234',
            email='info@pinevalley.com',
            website='https://pinevalley.com'
        )
    
    def test_create_organization_command_missing_name_fails(self):
        """Test CLI command fails when name is missing."""
        runner = CliRunner()
        result = runner.invoke(create_organization_command, [])
        
        assert result.exit_code == 2  # Click missing option error
        assert "Missing option '--name'" in result.output
    
    @patch('src.commands.create_organization.create_organization')
    def test_create_organization_command_duplicate_name_fails(self, mock_create_org):
        """Test CLI command fails when organization name exists."""
        mock_create_org.side_effect = click.ClickException("Organization with this name already exists")
        
        runner = CliRunner()
        result = runner.invoke(create_organization_command, [
            '--name', 'Existing Organization'
        ])
        
        assert result.exit_code == 1  # ClickException exit code
        assert "Organization with this name already exists" in result.output
    
    @patch('src.commands.create_organization.create_organization')
    def test_create_organization_command_empty_name_fails(self, mock_create_org):
        """Test CLI command fails when name is empty."""
        mock_create_org.side_effect = click.ClickException("Organization name cannot be empty")
        
        runner = CliRunner()
        result = runner.invoke(create_organization_command, [
            '--name', ''
        ])
        
        assert result.exit_code == 1
        assert "Organization name cannot be empty" in result.output
    
    @patch('src.commands.create_organization.create_organization')
    def test_create_organization_command_database_error_fails(self, mock_create_org):
        """Test CLI command handles database errors gracefully."""
        mock_create_org.side_effect = Exception("Database connection failed")
        
        runner = CliRunner()
        result = runner.invoke(create_organization_command, [
            '--name', 'Test Organization'
        ])
        
        assert result.exit_code == 1
        assert "Error: Database connection failed" in result.output


class TestCreateOrganizationEdgeCases:
    """Test edge cases for organization creation."""
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_case_insensitive_duplicate_check(self, mock_db_manager):
        """Test duplicate check is case-insensitive via database constraint."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock IntegrityError with unique constraint message (case insensitive)
        mock_session.commit.side_effect = IntegrityError("statement", "params", "UNIQUE constraint failed: organizations.name")
        
        with pytest.raises(click.ClickException, match="Organization with this name already exists"):
            create_organization("test organization")  # Different case
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_validate_organization_name_unicode_characters(self):
        """Test validation handles unicode characters."""
        unicode_name = "Boîte de Bowling Français"
        result = validate_organization_name(unicode_name)
        assert result == unicode_name
    
    def test_validate_organization_name_special_characters(self):
        """Test validation handles special characters."""
        special_name = "Smith & Jones Bowling Co. - Premium Lanes (Est. 1995)"
        result = validate_organization_name(special_name)
        assert result == special_name
    
    @patch('src.commands.create_organization.db_manager')
    def test_create_organization_handles_session_close_error(self, mock_db_manager):
        """Test organization creation handles session close errors gracefully."""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Mock organization doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        # Mock error on session close
        mock_session.close.side_effect = Exception("Session close error")
        
        # Should still succeed despite close error
        result = create_organization("Test Organization")
        
        assert isinstance(result, Organization)
        assert result.name == "Test Organization"
        
        # Verify database operations still occurred
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()