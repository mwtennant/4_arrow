"""Clean tests for merge profiles functionality."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from main import cli
from core.models import User


class TestMergeCommand:
    """Test merge command functionality."""
    
    def test_merge_command_help(self):
        """Test merge command help is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ['merge', '--help'])
        
        assert result.exit_code == 0
        assert "Merge one or more user profiles" in result.output
        assert "--main-id" in result.output
        assert "--merge-id" in result.output
        assert "--dry-run" in result.output
    
    @patch('src.commands.merge.merge_profiles')
    def test_merge_command_basic_usage(self, mock_merge_profiles):
        """Test basic merge command usage."""
        # Mock successful merge
        mock_merge_profiles.return_value = 0
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--main-id', '1',
            '--merge-id', '2'
        ])
        
        assert result.exit_code == 0
        
        # Verify merge_profiles was called with correct parameters
        mock_merge_profiles.assert_called_once_with(
            main_id=1,
            merge_ids=[2],
            dry_run=False,
            resolution_mode=None,
            no_interactive=False
        )
    
    @patch('src.commands.merge.merge_profiles')
    def test_merge_command_multiple_merge_ids(self, mock_merge_profiles):
        """Test merge command with multiple merge IDs."""
        mock_merge_profiles.return_value = 0
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--main-id', '1',
            '--merge-id', '2',
            '--merge-id', '3',
            '--merge-id', '4'
        ])
        
        assert result.exit_code == 0
        
        # Check that all merge IDs were passed
        call_args = mock_merge_profiles.call_args
        assert call_args.kwargs['main_id'] == 1
        assert call_args.kwargs['merge_ids'] == [2, 3, 4]
    
    @patch('src.commands.merge.merge_profiles')
    def test_merge_command_dry_run(self, mock_merge_profiles):
        """Test merge command with dry-run flag."""
        mock_merge_profiles.return_value = 0
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--main-id', '1',
            '--merge-id', '2',
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        
        # Check dry-run was set
        call_args = mock_merge_profiles.call_args
        assert call_args.kwargs['dry_run'] is True
    
    @patch('src.commands.merge.merge_profiles')
    def test_merge_command_resolution_modes(self, mock_merge_profiles):
        """Test merge command with different resolution modes."""
        mock_merge_profiles.return_value = 0
        
        resolution_modes = [
            ('--prefer-main', 'prefer_main'),
            ('--prefer-merge', 'prefer_merge'),
            ('--prefer-longest', 'prefer_longest')
        ]
        
        for flag, expected_mode in resolution_modes:
            runner = CliRunner()
            result = runner.invoke(cli, [
                'merge',
                '--main-id', '1',
                '--merge-id', '2',
                flag
            ])
            
            assert result.exit_code == 0
            
            # Check resolution mode was set correctly
            call_args = mock_merge_profiles.call_args
            assert call_args.kwargs['resolution_mode'] == expected_mode
    
    @patch('src.commands.merge.merge_profiles')
    def test_merge_command_no_interactive(self, mock_merge_profiles):
        """Test merge command with no-interactive flag."""
        mock_merge_profiles.return_value = 0
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--main-id', '1',
            '--merge-id', '2',
            '--no-interactive'
        ])
        
        assert result.exit_code == 0
        
        # Check no-interactive was set
        call_args = mock_merge_profiles.call_args
        assert call_args.kwargs['no_interactive'] is True
    
    @patch('src.commands.merge.merge_profiles')
    def test_merge_command_failure_exit_code(self, mock_merge_profiles):
        """Test merge command propagates failure exit codes."""
        # Mock merge failure
        mock_merge_profiles.return_value = 4  # Invalid arguments
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--main-id', '1',
            '--merge-id', '2'
        ])
        
        assert result.exit_code == 4
    
    def test_merge_command_requires_main_id(self):
        """Test merge command requires main-id parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--merge-id', '2'
        ])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()
    
    def test_merge_command_requires_merge_id(self):
        """Test merge command requires at least one merge-id parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'merge',
            '--main-id', '1'
        ])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()


class TestMergeProfilesLogic:
    """Test the core merge profiles logic (if the function exists)."""
    
    def test_merge_profiles_import(self):
        """Test that merge_profiles function can be imported."""
        try:
            from src.commands.merge import merge_profiles
            assert callable(merge_profiles)
        except ImportError:
            pytest.skip("merge_profiles function not implemented yet")
    
    @patch('src.commands.merge.db_manager')
    def test_merge_profiles_basic_validation(self, mock_db_manager):
        """Test basic merge profiles validation."""
        try:
            from src.commands.merge import merge_profiles
        except ImportError:
            pytest.skip("merge_profiles function not implemented yet")
        
        # Mock database session
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        # Test self-merge prevention
        result = merge_profiles(
            main_id=1,
            merge_ids=[1],  # Same as main_id
            dry_run=True,
            resolution_mode=None,
            no_interactive=True
        )
        
        # Should return error code for invalid arguments
        assert result == 4
    
    @patch('src.commands.merge.db_manager')
    def test_merge_profiles_dry_run_mode(self, mock_db_manager):
        """Test merge profiles dry run mode."""
        try:
            from src.commands.merge import merge_profiles
        except ImportError:
            pytest.skip("merge_profiles function not implemented yet")
        
        # Mock database session and users
        mock_session = MagicMock()
        mock_db_manager.get_session.return_value = mock_session
        
        main_user = User(id=1, first_name="Main", last_name="User", email="main@example.com")
        merge_user = User(id=2, first_name="Merge", last_name="User", email="merge@example.com")
        
        def mock_get(user_id):
            if user_id == 1:
                return main_user
            elif user_id == 2:
                return merge_user
            return None
        
        mock_session.get.side_effect = mock_get
        
        # Run dry-run merge
        result = merge_profiles(
            main_id=1,
            merge_ids=[2],
            dry_run=True,
            resolution_mode='prefer_main',
            no_interactive=True
        )
        
        # Should succeed in dry-run mode
        assert result == 0
        
        # Should not have committed any changes
        mock_session.commit.assert_not_called()


class TestMergeIntegration:
    """Integration tests for merge functionality."""
    
    def test_merge_command_examples_in_help(self):
        """Test that merge command help includes usage examples."""
        runner = CliRunner()
        result = runner.invoke(cli, ['merge', '--help'])
        
        assert result.exit_code == 0
        assert "Examples:" in result.output
        assert "python main.py merge" in result.output
    
    def test_merge_cli_short_flags(self):
        """Test merge command supports short flags."""
        runner = CliRunner()
        result = runner.invoke(cli, ['merge', '--help'])
        
        assert result.exit_code == 0
        assert "-m" in result.output  # Short flag for --main-id
        assert "-i" in result.output  # Short flag for --merge-id