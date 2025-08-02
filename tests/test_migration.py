"""Tests for role terminology migration script."""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from scripts.migrate_role_terminology import RoleTerminologyMigration
from core.models import User, ProfileRole


class TestRoleTerminologyMigration:
    """Test the role terminology migration functionality."""
    
    def test_check_migration_status_no_role_column(self):
        """Test status check when role column doesn't exist."""
        with patch('scripts.migrate_role_terminology.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            # Mock inspector to show no role column
            mock_inspector = MagicMock()
            mock_inspector.get_columns.return_value = [
                {'name': 'id'}, {'name': 'email'}, {'name': 'first_name'}
            ]
            
            with patch('scripts.migrate_role_terminology.inspect', return_value=mock_inspector):
                migration = RoleTerminologyMigration(dry_run=True)
                migration.session = mock_session
                
                # Mock user count
                mock_session.query.return_value.count.return_value = 0
                
                status = migration.check_migration_status()
                
                assert status['has_role_column'] is False
                assert status['has_is_member_column'] is False
                assert status['migration_needed'] is True
                assert status['total_users'] == 0
    
    def test_check_migration_status_with_role_column(self):
        """Test status check when role column exists."""
        with patch('scripts.migrate_role_terminology.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_db
            
            mock_inspector = MagicMock()
            mock_inspector.get_columns.return_value = [
                {'name': 'id'}, {'name': 'email'}, {'name': 'role'}
            ]
            
            with patch('scripts.migrate_role_terminology.inspect', return_value=mock_inspector):
                migration = RoleTerminologyMigration(dry_run=True)
                migration.session = mock_session
                
                # Mock users with roles
                mock_user1 = MagicMock()
                mock_user1.get_role.return_value = ProfileRole.REGISTERED_USER
                mock_user2 = MagicMock()
                mock_user2.get_role.return_value = ProfileRole.UNREGISTERED_USER
                
                mock_session.query.return_value.count.return_value = 2
                mock_session.query.return_value.all.return_value = [mock_user1, mock_user2]
                
                status = migration.check_migration_status()
                
                assert status['has_role_column'] is True
                assert status['migration_needed'] is False
                assert status['total_users'] == 2
                assert status['role_distribution']['registered_user'] == 1
                assert status['role_distribution']['unregistered_user'] == 1
    
    def test_add_role_column_dry_run(self):
        """Test adding role column in dry run mode."""
        migration = RoleTerminologyMigration(dry_run=True)
        mock_session = MagicMock()
        migration.session = mock_session
        
        # Should not execute any SQL in dry run
        migration.add_role_column()
        
        mock_session.execute.assert_not_called()
        mock_session.commit.assert_not_called()
    
    def test_add_role_column_success(self):
        """Test successfully adding role column."""
        migration = RoleTerminologyMigration(dry_run=False)
        mock_session = MagicMock()
        migration.session = mock_session
        
        migration.add_role_column()
        
        # Should execute ALTER TABLE statements
        assert mock_session.execute.call_count == 2
        mock_session.commit.assert_called_once()
    
    def test_add_role_column_already_exists(self):
        """Test handling when role column already exists."""
        migration = RoleTerminologyMigration(dry_run=False)
        mock_session = MagicMock()
        migration.session = mock_session
        
        # Mock SQLAlchemy error for existing column
        mock_session.execute.side_effect = SQLAlchemyError("column already exists")
        
        # Should not raise exception
        migration.add_role_column()
        
        mock_session.rollback.assert_called_once()
    
    def test_backfill_role_data(self):
        """Test backfilling role data based on user profiles."""
        migration = RoleTerminologyMigration(dry_run=True)
        mock_session = MagicMock()
        migration.session = mock_session
        
        # Create mock users with different profiles
        mock_user1 = MagicMock()
        mock_user1.id = 1
        mock_user1.email = "user@example.com"
        mock_user1.get_role.return_value = ProfileRole.REGISTERED_USER
        
        mock_user2 = MagicMock()
        mock_user2.id = 2 
        mock_user2.email = None
        mock_user2.get_role.return_value = ProfileRole.UNREGISTERED_USER
        
        mock_user3 = MagicMock()
        mock_user3.id = 3
        mock_user3.email = "admin@tournamentorg.com"
        mock_user3.get_role.return_value = ProfileRole.ORG_MEMBER
        
        mock_session.query.return_value.all.return_value = [mock_user1, mock_user2, mock_user3]
        
        updates = migration.backfill_role_data()
        
        assert len(updates) == 3
        assert updates[0] == (1, "member (has email)", "registered_user")
        assert updates[1] == (2, "non-member (no email)", "unregistered_user") 
        assert updates[2] == (3, "admin/org_member", "org_member")
        
        # Should not execute updates in dry run
        mock_session.execute.assert_not_called()
    
    def test_backfill_role_data_real_execution(self):
        """Test backfilling with real database execution."""
        migration = RoleTerminologyMigration(dry_run=False)
        mock_session = MagicMock()
        migration.session = mock_session
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.get_role.return_value = ProfileRole.REGISTERED_USER
        
        mock_session.query.return_value.all.return_value = [mock_user]
        
        updates = migration.backfill_role_data()
        
        assert len(updates) == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    def test_verify_migration_success(self):
        """Test successful migration verification."""
        migration = RoleTerminologyMigration(dry_run=False)
        mock_session = MagicMock()
        migration.session = mock_session
        
        # Mock no invalid roles
        mock_session.execute.return_value.fetchall.return_value = []
        mock_session.execute.return_value.scalar.return_value = 5
        
        result = migration.verify_migration()
        
        assert result is True
    
    def test_verify_migration_invalid_roles(self):
        """Test migration verification with invalid roles."""
        migration = RoleTerminologyMigration(dry_run=False)
        mock_session = MagicMock()
        migration.session = mock_session
        
        # Mock invalid roles found
        mock_session.execute.return_value.fetchall.return_value = [
            (1, 'invalid_role'), (2, None)
        ]
        
        result = migration.verify_migration()
        
        assert result is False
    
    def test_run_forward_migration_already_completed(self):
        """Test running migration when already completed."""
        with patch('scripts.migrate_role_terminology.db_manager'):
            migration = RoleTerminologyMigration(dry_run=True)
            mock_session = MagicMock()
            migration.session = mock_session
            
            # Mock already completed status
            with patch.object(migration, 'check_migration_status') as mock_status:
                mock_status.return_value = {
                    'migration_needed': False,
                    'total_users': 10,
                    'has_role_column': True,
                    'has_is_member_column': False,
                    'role_distribution': {'registered_user': 10}
                }
                
                result = migration.run_forward_migration()
                
                assert result is True
    
    def test_run_forward_migration_full_process(self):
        """Test running complete forward migration process."""
        with patch('scripts.migrate_role_terminology.db_manager'):
            migration = RoleTerminologyMigration(dry_run=True)
            mock_session = MagicMock()
            migration.session = mock_session
            
            # Mock migration needed
            with patch.object(migration, 'check_migration_status') as mock_status, \
                 patch.object(migration, 'add_role_column') as mock_add_col, \
                 patch.object(migration, 'backfill_role_data') as mock_backfill, \
                 patch.object(migration, 'create_performance_index') as mock_index:
                
                mock_status.return_value = {
                    'migration_needed': True,
                    'total_users': 5,
                    'has_role_column': False,
                    'has_is_member_column': True,
                    'role_distribution': {}
                }
                mock_backfill.return_value = [(1, 'old', 'new')]
                
                result = migration.run_forward_migration()
                
                assert result is True
                mock_add_col.assert_called_once()
                mock_backfill.assert_called_once()
                mock_index.assert_called_once()
    
    def test_run_reverse_migration_dry_run(self):
        """Test reverse migration in dry run mode."""
        migration = RoleTerminologyMigration(dry_run=True)
        mock_session = MagicMock()
        migration.session = mock_session
        
        result = migration.run_reverse_migration()
        
        assert result is True
        mock_session.execute.assert_not_called()
    
    def test_context_manager(self):
        """Test migration as context manager."""
        with patch('scripts.migrate_role_terminology.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            with RoleTerminologyMigration() as migration:
                assert migration.session == mock_session
            
            mock_session.close.assert_called_once()
    
    def test_context_manager_with_exception(self):
        """Test context manager handles exceptions properly."""
        with patch('scripts.migrate_role_terminology.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            try:
                with RoleTerminologyMigration() as migration:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()