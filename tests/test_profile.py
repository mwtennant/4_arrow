"""Tests for profile management functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from core.profile import get_profile, edit_profile, delete_profile
from core.models import User
from main import cli


class TestProfileFunctions:
    """Test the core profile management functions."""
    
    def test_get_profile_by_user_id(self):
        """Test getting profile by user ID."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            address="123 Main St",
            usbc_id="123456",
            tnba_id="654321"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            result = get_profile(user_id=1)
            assert result == mock_user
            mock_session.close.assert_called_once()
    
    def test_get_profile_by_email(self):
        """Test getting profile by email."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            result = get_profile(email="test@example.com")
            assert result == mock_user
            mock_session.close.assert_called_once()
    
    def test_get_profile_by_usbc_id(self):
        """Test getting profile by USBC ID."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            usbc_id="123456"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            result = get_profile(usbc_id="123456")
            assert result == mock_user
            mock_session.close.assert_called_once()
    
    def test_get_profile_by_tnba_id(self):
        """Test getting profile by TNBA ID."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            tnba_id="654321"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            result = get_profile(tnba_id="654321")
            assert result == mock_user
            mock_session.close.assert_called_once()
    
    def test_get_profile_not_found(self):
        """Test getting profile that doesn't exist."""
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            result = get_profile(user_id=999)
            assert result is None
            mock_session.close.assert_called_once()
    
    def test_edit_profile_success(self):
        """Test successful profile editing."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            result = edit_profile(user_id=1, first="Jane", phone="555-5678")
            assert result is True
            assert mock_user.first_name == "Jane"
            assert mock_user.phone == "555-5678"
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
    
    def test_edit_profile_user_not_found(self):
        """Test editing profile for non-existent user."""
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            result = edit_profile(user_id=999, first="Jane")
            assert result is False
            mock_session.close.assert_called_once()
    
    def test_edit_profile_empty_string_validation(self):
        """Test that empty strings are rejected."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            with pytest.raises(ValueError, match="First name cannot be empty"):
                edit_profile(user_id=1, first="")
            
            mock_session.close.assert_called_once()
    
    def test_delete_profile_success(self):
        """Test successful profile deletion."""
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = mock_user
            
            result = delete_profile(user_id=1)
            assert result is True
            mock_session.delete.assert_called_once_with(mock_user)
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
    
    def test_delete_profile_user_not_found(self):
        """Test deleting profile for non-existent user."""
        with patch('core.profile.db_manager.get_session') as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            result = delete_profile(user_id=999)
            assert result is False
            mock_session.close.assert_called_once()


class TestProfileCLI:
    """Test the CLI commands for profile management."""
    
    def test_get_profile_by_user_id_success(self):
        """Test get-profile command with user ID."""
        runner = CliRunner()
        
        with patch('main.get_profile') as mock_get_profile, \
             patch('main.display_profile') as mock_display:
            
            mock_user = User(id=1, email="test@example.com", first_name="John", last_name="Doe", phone="555-1234")
            mock_get_profile.return_value = mock_user
            
            result = runner.invoke(cli, ['get-profile', '--user-id', '1'])
            
            assert result.exit_code == 0
            mock_get_profile.assert_called_once_with(user_id=1, email=None, usbc_id=None, tnba_id=None)
            mock_display.assert_called_once_with(mock_user)
    
    def test_get_profile_by_email_success(self):
        """Test get-profile command with email."""
        runner = CliRunner()
        
        with patch('main.get_profile') as mock_get_profile, \
             patch('main.display_profile') as mock_display:
            
            mock_user = User(id=1, email="test@example.com", first_name="John", last_name="Doe", phone="555-1234")
            mock_get_profile.return_value = mock_user
            
            result = runner.invoke(cli, ['get-profile', '--email', 'test@example.com'])
            
            assert result.exit_code == 0
            mock_get_profile.assert_called_once_with(user_id=None, email="test@example.com", usbc_id=None, tnba_id=None)
            mock_display.assert_called_once_with(mock_user)
    
    def test_get_profile_by_usbc_id_success(self):
        """Test get-profile command with USBC ID."""
        runner = CliRunner()
        
        with patch('main.get_profile') as mock_get_profile, \
             patch('main.display_profile') as mock_display:
            
            mock_user = User(id=1, email="test@example.com", first_name="John", last_name="Doe", phone="555-1234")
            mock_get_profile.return_value = mock_user
            
            result = runner.invoke(cli, ['get-profile', '--usbc_id', '123456'])
            
            assert result.exit_code == 0
            mock_get_profile.assert_called_once_with(user_id=None, email=None, usbc_id="123456", tnba_id=None)
            mock_display.assert_called_once_with(mock_user)
    
    def test_get_profile_by_tnba_id_success(self):
        """Test get-profile command with TNBA ID."""
        runner = CliRunner()
        
        with patch('main.get_profile') as mock_get_profile, \
             patch('main.display_profile') as mock_display:
            
            mock_user = User(id=1, email="test@example.com", first_name="John", last_name="Doe", phone="555-1234")
            mock_get_profile.return_value = mock_user
            
            result = runner.invoke(cli, ['get-profile', '--tnba_id', '654321'])
            
            assert result.exit_code == 0
            mock_get_profile.assert_called_once_with(user_id=None, email=None, usbc_id=None, tnba_id="654321")
            mock_display.assert_called_once_with(mock_user)
    
    def test_get_profile_with_two_id_flags(self):
        """Test get-profile command with two ID flags (should fail)."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['get-profile', '--user-id', '1', '--email', 'test@example.com'])
        
        assert result.exit_code == 1
        assert "ERROR: Exactly one ID flag must be provided" in result.output
    
    def test_get_profile_no_id_flags(self):
        """Test get-profile command with no ID flags (should fail)."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['get-profile'])
        
        assert result.exit_code == 1
        assert "ERROR: Exactly one ID flag must be provided" in result.output
    
    def test_get_profile_not_found(self):
        """Test get-profile command for non-existent user."""
        runner = CliRunner()
        
        with patch('main.get_profile') as mock_get_profile:
            mock_get_profile.return_value = None
            
            result = runner.invoke(cli, ['get-profile', '--user-id', '999'])
            
            assert result.exit_code == 1
            assert "ERROR: No user found." in result.output
    
    def test_edit_profile_success(self):
        """Test edit-profile command success."""
        runner = CliRunner()
        
        with patch('main.edit_profile') as mock_edit_profile:
            mock_edit_profile.return_value = True
            
            result = runner.invoke(cli, ['edit-profile', '--user-id', '1', '--first', 'Jane'])
            
            assert result.exit_code == 0
            assert "Profile updated." in result.output
            mock_edit_profile.assert_called_once_with(user_id=1, first="Jane", last=None, phone=None, address=None)
    
    def test_edit_profile_user_not_found(self):
        """Test edit-profile command for non-existent user."""
        runner = CliRunner()
        
        with patch('main.edit_profile') as mock_edit_profile:
            mock_edit_profile.return_value = False
            
            result = runner.invoke(cli, ['edit-profile', '--user-id', '999', '--first', 'Jane'])
            
            assert result.exit_code == 1
            assert "ERROR: User not found" in result.output
    
    def test_edit_profile_no_fields(self):
        """Test edit-profile command with no fields (should fail)."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['edit-profile', '--user-id', '1'])
        
        assert result.exit_code == 1
        assert "ERROR: At least one field must be provided" in result.output
    
    def test_edit_profile_empty_string_error(self):
        """Test edit-profile command with empty string."""
        runner = CliRunner()
        
        with patch('main.edit_profile') as mock_edit_profile:
            mock_edit_profile.side_effect = ValueError("First name cannot be empty")
            
            result = runner.invoke(cli, ['edit-profile', '--user-id', '1', '--first', ''])
            
            assert result.exit_code == 1
            assert "ERROR: First name cannot be empty" in result.output
    
    def test_delete_profile_success(self):
        """Test delete-profile command success."""
        runner = CliRunner()
        
        with patch('main.delete_profile') as mock_delete_profile:
            mock_delete_profile.return_value = True
            
            result = runner.invoke(cli, ['delete-profile', '--user-id', '1', '--confirm', 'yes'])
            
            assert result.exit_code == 0
            assert "Profile deleted." in result.output
            mock_delete_profile.assert_called_once_with(1)
    
    def test_delete_profile_user_not_found(self):
        """Test delete-profile command for non-existent user."""
        runner = CliRunner()
        
        with patch('main.delete_profile') as mock_delete_profile:
            mock_delete_profile.return_value = False
            
            result = runner.invoke(cli, ['delete-profile', '--user-id', '999', '--confirm', 'yes'])
            
            assert result.exit_code == 1
            assert "ERROR: User not found" in result.output
    
    def test_delete_profile_without_confirm(self):
        """Test delete-profile command without confirmation."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['delete-profile', '--user-id', '1'])
        
        assert result.exit_code == 1
        assert "ERROR: Deletion aborted." in result.output
    
    def test_delete_profile_wrong_confirm(self):
        """Test delete-profile command with wrong confirmation."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['delete-profile', '--user-id', '1', '--confirm', 'no'])
        
        assert result.exit_code == 1
        assert "ERROR: Deletion aborted." in result.output