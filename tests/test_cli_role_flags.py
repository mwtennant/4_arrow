"""Tests for CLI role flag migration and backward compatibility."""

import warnings
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

from main import cli


class TestCliRoleFlags:
    """Test CLI role flag migration and deprecation warnings."""
    
    def test_new_role_flag_works(self):
        """Test that --role flag works with new values."""
        runner = CliRunner()
        
        with patch('src.commands.list_users.list_users_enhanced') as mock_list_users, \
             patch('utils.csv_writer.validate_csv_path'), \
             patch('src.commands.list_users.parse_date_filter'):
            
            mock_list_users.return_value = []
            
            # Test each role value
            for role in ['registered_user', 'unregistered_user', 'org_member']:
                result = runner.invoke(cli, ['list-users', '--role', role])
                assert result.exit_code == 0
                
                # Verify the role was passed correctly
                call_args = mock_list_users.call_args
                assert call_args is not None
                assert call_args.kwargs['role'].value == role
    
    def test_legacy_member_flag_shows_deprecation_warning(self):
        """Test that --member flag shows deprecation warning."""
        runner = CliRunner()
        
        with patch('src.commands.list_users.list_users_enhanced') as mock_list_users, \
             patch('utils.csv_writer.validate_csv_path'), \
             patch('src.commands.list_users.parse_date_filter'), \
             warnings.catch_warnings(record=True) as w:
            
            warnings.simplefilter("always")
            mock_list_users.return_value = []
            
            result = runner.invoke(cli, ['list-users', '--member'])
            
            # Command should succeed
            assert result.exit_code == 0
            
            # Should have issued a deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "--member flag is deprecated" in str(w[0].message)
            assert "Use --role registered_user instead" in str(w[0].message)
            
            # Should have called with registered_user role
            call_args = mock_list_users.call_args
            assert call_args is not None
            assert call_args.kwargs['role'].value == 'registered_user'
    
    def test_cannot_use_both_member_and_role_flags(self):
        """Test that using both --member and --role flags returns error."""
        runner = CliRunner()
        
        with patch('src.commands.list_users.list_users_enhanced'), \
             patch('utils.csv_writer.validate_csv_path'), \
             patch('src.commands.list_users.parse_date_filter'):
            
            result = runner.invoke(cli, ['list-users', '--member', '--role', 'unregistered_user'])
            
            # Should exit with error code 4
            assert result.exit_code == 4
            assert "Cannot use both --member and --role flags" in result.output
    
    def test_member_flag_maps_to_registered_user(self):
        """Test that --member flag maps to registered_user role."""
        runner = CliRunner()
        
        with patch('src.commands.list_users.list_users_enhanced') as mock_list_users, \
             patch('utils.csv_writer.validate_csv_path'), \
             patch('src.commands.list_users.parse_date_filter'), \
             warnings.catch_warnings():
            
            warnings.simplefilter("ignore")  # Suppress warnings for this test
            mock_list_users.return_value = []
            
            result = runner.invoke(cli, ['list-users', '--member'])
            
            assert result.exit_code == 0
            
            # Verify it was called with registered_user role
            call_args = mock_list_users.call_args
            assert call_args is not None
            assert call_args.kwargs['role'].value == 'registered_user'
    
    def test_help_text_shows_deprecation_notice(self):
        """Test that help text shows deprecation notice for --member flag."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['list-users', '--help'])
        
        assert result.exit_code == 0
        assert "[DEPRECATED]" in result.output
        assert "--member" in result.output
        assert "Use --role registered_user instead" in result.output
    
    def test_role_flag_without_member_works_normally(self):
        """Test that --role flag works normally when --member is not used."""
        runner = CliRunner()
        
        with patch('src.commands.list_users.list_users_enhanced') as mock_list_users, \
             patch('utils.csv_writer.validate_csv_path'), \
             patch('src.commands.list_users.parse_date_filter'), \
             warnings.catch_warnings(record=True) as w:
            
            warnings.simplefilter("always")
            mock_list_users.return_value = []
            
            result = runner.invoke(cli, ['list-users', '--role', 'org_member'])
            
            assert result.exit_code == 0
            
            # Should not have any warnings
            assert len(w) == 0
            
            # Should call with org_member role
            call_args = mock_list_users.call_args
            assert call_args is not None
            assert call_args.kwargs['role'].value == 'org_member'
    
    def test_no_role_flags_works_normally(self):
        """Test that command works normally when no role flags are provided."""
        runner = CliRunner()
        
        with patch('src.commands.list_users.list_users_enhanced') as mock_list_users, \
             patch('utils.csv_writer.validate_csv_path'), \
             patch('src.commands.list_users.parse_date_filter'), \
             warnings.catch_warnings(record=True) as w:
            
            warnings.simplefilter("always")
            mock_list_users.return_value = []
            
            result = runner.invoke(cli, ['list-users'])
            
            assert result.exit_code == 0
            
            # Should not have any warnings
            assert len(w) == 0
            
            # Should call with None role
            call_args = mock_list_users.call_args
            assert call_args is not None
            assert call_args.kwargs['role'] is None


class TestCliIntegration:
    """Integration tests for CLI role flags with actual database."""
    
    @patch('storage.database.db_manager.get_session')
    def test_member_flag_integration(self, mock_get_session):
        """Integration test for --member flag with mocked database."""
        runner = CliRunner()
        
        # Mock session and query
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            result = runner.invoke(cli, ['list-users', '--member'])
            
            # Should succeed (may show "No users found" but that's OK)
            assert result.exit_code == 0
            
            # Should have deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            
            # Should have called database
            assert mock_session.query.called
            assert mock_session.close.called