"""Tests for legacy JSON import/export shim."""

import pytest
import warnings
from core.models import ProfileRole
from utils.legacy_shim import (
    LegacyRoleShim, 
    export_users_to_json_with_legacy,
    import_users_from_json_with_legacy,
    LEGACY_FIELD_MAPPING
)


class TestLegacyRoleShim:
    """Test the legacy role shim functionality."""
    
    def test_export_registered_user(self):
        """Test exporting registered user with legacy field."""
        user_data = {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'registered_user'
        }
        
        result = LegacyRoleShim.export_user_with_legacy_fields(user_data)
        
        assert result['id'] == 1
        assert result['name'] == 'John Doe'
        assert result['email'] == 'john@example.com'
        assert result['role'] == 'registered_user'
        assert result['is_member'] is True
    
    def test_export_unregistered_user(self):
        """Test exporting unregistered user with legacy field."""
        user_data = {
            'id': 2,
            'name': 'Jane Smith',
            'role': 'unregistered_user'
        }
        
        result = LegacyRoleShim.export_user_with_legacy_fields(user_data)
        
        assert result['is_member'] is False
    
    def test_export_org_member(self):
        """Test exporting org member with legacy field."""
        user_data = {
            'id': 3,
            'name': 'Admin User',
            'email': 'admin@tournamentorg.com',
            'role': 'org_member'
        }
        
        result = LegacyRoleShim.export_user_with_legacy_fields(user_data)
        
        assert result['is_member'] is False  # Org members map to is_member=False
    
    def test_export_no_role(self):
        """Test exporting user with no role field."""
        user_data = {
            'id': 4,
            'name': 'Unknown User'
        }
        
        result = LegacyRoleShim.export_user_with_legacy_fields(user_data)
        
        assert result['is_member'] is False
    
    def test_export_preserves_original(self):
        """Test that export doesn't modify original data."""
        original = {
            'id': 1,
            'role': 'registered_user'
        }
        
        result = LegacyRoleShim.export_user_with_legacy_fields(original)
        
        # Original should be unchanged
        assert 'is_member' not in original
        assert result is not original
    
    def test_import_legacy_member_true(self):
        """Test importing user with is_member=True."""
        import_data = {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'is_member': True
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'registered_user'
        assert 'is_member' not in result
    
    def test_import_legacy_member_false_with_email(self):
        """Test importing user with is_member=False but has email."""
        import_data = {
            'id': 2,
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'is_member': False
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'registered_user'
        assert 'is_member' not in result
    
    def test_import_legacy_member_false_org_email(self):
        """Test importing user with org email and is_member=False."""
        import_data = {
            'id': 3,
            'name': 'Admin User',
            'email': 'admin@tournamentorg.com',
            'is_member': False
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'org_member'
        assert 'is_member' not in result
    
    def test_import_legacy_no_email(self):
        """Test importing user with no email."""
        import_data = {
            'id': 4,
            'name': 'Tournament Only',
            'is_member': False
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'unregistered_user'
        assert 'is_member' not in result
    
    def test_import_existing_role_takes_precedence(self):
        """Test that existing role field takes precedence over is_member."""
        import_data = {
            'id': 5,
            'name': 'User',
            'email': 'user@example.com',
            'role': 'org_member',
            'is_member': True  # Should be ignored
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'org_member'
        assert 'is_member' not in result
    
    def test_import_invalid_role_uses_legacy(self):
        """Test that invalid role field falls back to legacy logic."""
        import_data = {
            'id': 6,
            'name': 'User',
            'email': 'user@example.com',
            'role': 'invalid_role',
            'is_member': True
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'registered_user'
        assert 'is_member' not in result
    
    def test_import_whitespace_email(self):
        """Test importing user with whitespace-only email."""
        import_data = {
            'id': 7,
            'name': 'User',
            'email': '   ',
            'is_member': False
        }
        
        result = LegacyRoleShim.import_user_with_legacy_fields(import_data)
        
        assert result['role'] == 'unregistered_user'
    
    def test_bulk_export(self):
        """Test bulk export of users."""
        users = [
            {'id': 1, 'role': 'registered_user'},
            {'id': 2, 'role': 'unregistered_user'},
            {'id': 3, 'role': 'org_member'}
        ]
        
        result = LegacyRoleShim.bulk_export_users_with_legacy(users)
        
        assert len(result) == 3
        assert result[0]['is_member'] is True
        assert result[1]['is_member'] is False
        assert result[2]['is_member'] is False
    
    def test_bulk_import(self):
        """Test bulk import of users."""
        import_users = [
            {'id': 1, 'email': 'user1@example.com', 'is_member': True},
            {'id': 2, 'is_member': False},
            {'id': 3, 'email': 'admin@tournamentorg.com', 'is_member': False}
        ]
        
        result = LegacyRoleShim.bulk_import_users_with_legacy(import_users)
        
        assert len(result) == 3
        assert result[0]['role'] == 'registered_user'
        assert result[1]['role'] == 'unregistered_user'
        assert result[2]['role'] == 'org_member'
        
        # Should remove all is_member fields
        for user in result:
            assert 'is_member' not in user
    
    def test_deprecation_warning(self):
        """Test that deprecation warning is issued."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            LegacyRoleShim.warn_about_legacy_usage("test context")
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "Legacy 'is_member' field used in test context" in str(w[0].message)
            assert "Please update to use 'role' field" in str(w[0].message)
    
    def test_convenience_export_function_with_warning(self):
        """Test convenience export function issues warning."""
        users = [{'id': 1, 'role': 'registered_user'}]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            result = export_users_to_json_with_legacy(users, warn=True)
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert result[0]['is_member'] is True
    
    def test_convenience_export_function_no_warning(self):
        """Test convenience export function without warning."""
        users = [{'id': 1, 'role': 'registered_user'}]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            result = export_users_to_json_with_legacy(users, warn=False)
            
            assert len(w) == 0
            assert result[0]['is_member'] is True
    
    def test_convenience_import_function_with_warning(self):
        """Test convenience import function issues warning."""
        import_data = [{'id': 1, 'email': 'user@example.com', 'is_member': True}]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            result = import_users_from_json_with_legacy(import_data, warn=True)
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert result[0]['role'] == 'registered_user'
    
    def test_convenience_import_function_no_warning(self):
        """Test convenience import function without warning."""
        import_data = [{'id': 1, 'email': 'user@example.com', 'is_member': True}]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            result = import_users_from_json_with_legacy(import_data, warn=False)
            
            assert len(w) == 0
            assert result[0]['role'] == 'registered_user'
    
    def test_legacy_field_mapping_constant(self):
        """Test that legacy field mapping constant is properly defined."""
        assert 'is_member' in LEGACY_FIELD_MAPPING
        mapping = LEGACY_FIELD_MAPPING['is_member']
        
        assert mapping['legacy_type'] == 'boolean'
        assert mapping['new_field'] == 'role'
        assert mapping['new_type'] == 'string'
        assert 'registered_user' in mapping['valid_values']
        assert 'unregistered_user' in mapping['valid_values']
        assert 'org_member' in mapping['valid_values']
        assert 'mapping_rules' in mapping
    
    def test_round_trip_consistency(self):
        """Test that export->import round trip maintains consistency."""
        original_users = [
            {'id': 1, 'name': 'User1', 'email': 'user1@example.com', 'role': 'registered_user'},
            {'id': 2, 'name': 'User2', 'role': 'unregistered_user'},
            {'id': 3, 'name': 'Admin', 'email': 'admin@tournamentorg.com', 'role': 'org_member'}
        ]
        
        # Export with legacy fields
        exported = LegacyRoleShim.bulk_export_users_with_legacy(original_users)
        
        # Remove role field to simulate external system
        for user in exported:
            user.pop('role')
        
        # Import back from legacy
        imported = LegacyRoleShim.bulk_import_users_with_legacy(exported)
        
        # Should have same roles as original
        for orig, imp in zip(original_users, imported):
            assert orig['role'] == imp['role']
            assert orig['id'] == imp['id']
            assert orig['name'] == imp['name']