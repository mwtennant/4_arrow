"""Legacy shim for JSON import/export compatibility.

This module provides translation between old and new role terminology
for external systems that still expect the legacy `is_member` field.
"""

import warnings
from typing import Dict, Any, List, Union
from core.models import ProfileRole


class LegacyRoleShim:
    """Handles translation between legacy and new role terminology."""
    
    @staticmethod
    def export_user_with_legacy_fields(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert user data to include legacy is_member field for export.
        
        Args:
            user_data: User data dictionary with 'role' field
            
        Returns:
            Dict with legacy 'is_member' field added
        """
        # Make a copy to avoid modifying original
        export_data = user_data.copy()
        
        # Map role to legacy is_member field
        role = user_data.get('role')
        if role:
            # Only registered_user maps to is_member=True
            # org_member and unregistered_user map to is_member=False
            export_data['is_member'] = (role == ProfileRole.REGISTERED_USER.value)
        else:
            # Default to False if no role specified
            export_data['is_member'] = False
        
        return export_data
    
    @staticmethod
    def import_user_with_legacy_fields(import_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert imported user data from legacy is_member to new role field.
        
        Args:
            import_data: User data dictionary that may contain 'is_member' field
            
        Returns:
            Dict with 'role' field derived from legacy data
        """
        # Make a copy to avoid modifying original
        user_data = import_data.copy()
        
        # If role is already present, prefer it over is_member
        if 'role' in user_data and user_data['role'] in [role.value for role in ProfileRole]:
            # Valid role already present, just remove is_member if it exists
            user_data.pop('is_member', None)
            return user_data
        
        # Derive role from legacy is_member field
        is_member = import_data.get('is_member')
        email = import_data.get('email')
        
        if is_member is True:
            # Legacy member means registered user
            user_data['role'] = ProfileRole.REGISTERED_USER.value
        elif email and str(email).strip():
            # Has email but is_member is False/None - could be org member
            email_str = str(email).lower()
            if email_str.endswith('@tournamentorg.com') or email_str.endswith('@admin.com'):
                user_data['role'] = ProfileRole.ORG_MEMBER.value
            else:
                user_data['role'] = ProfileRole.REGISTERED_USER.value
        else:
            # No email - unregistered user
            user_data['role'] = ProfileRole.UNREGISTERED_USER.value
        
        # Remove legacy field to avoid confusion
        user_data.pop('is_member', None)
        
        return user_data
    
    @staticmethod
    def bulk_export_users_with_legacy(users_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Export multiple users with legacy field mapping.
        
        Args:
            users_data: List of user data dictionaries
            
        Returns:
            List of user data with legacy fields added
        """
        return [
            LegacyRoleShim.export_user_with_legacy_fields(user) 
            for user in users_data
        ]
    
    @staticmethod
    def bulk_import_users_with_legacy(import_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Import multiple users with legacy field translation.
        
        Args:
            import_data: List of user data dictionaries that may contain legacy fields
            
        Returns:
            List of user data with role fields derived from legacy data
        """
        return [
            LegacyRoleShim.import_user_with_legacy_fields(user) 
            for user in import_data
        ]
    
    @staticmethod
    def warn_about_legacy_usage(context: str = "JSON operation") -> None:
        """Issue deprecation warning about legacy field usage.
        
        Args:
            context: Description of where the legacy usage occurred
        """
        warnings.warn(
            f"Legacy 'is_member' field used in {context}. "
            "Please update to use 'role' field with values: "
            "registered_user, unregistered_user, org_member",
            DeprecationWarning,
            stacklevel=3
        )


# Convenience functions for common use cases
def export_users_to_json_with_legacy(users_data: List[Dict[str, Any]], 
                                    warn: bool = True) -> List[Dict[str, Any]]:
    """Export users to JSON format with legacy compatibility.
    
    Args:
        users_data: List of user dictionaries
        warn: Whether to issue deprecation warning
        
    Returns:
        List of user dictionaries with legacy is_member field
    """
    if warn:
        LegacyRoleShim.warn_about_legacy_usage("JSON export")
    
    return LegacyRoleShim.bulk_export_users_with_legacy(users_data)


def import_users_from_json_with_legacy(import_data: List[Dict[str, Any]], 
                                     warn: bool = True) -> List[Dict[str, Any]]:
    """Import users from JSON format with legacy compatibility.
    
    Args:
        import_data: List of user dictionaries that may contain legacy fields
        warn: Whether to issue deprecation warning
        
    Returns:
        List of user dictionaries with role field derived from legacy data
    """
    if warn:
        LegacyRoleShim.warn_about_legacy_usage("JSON import")
    
    return LegacyRoleShim.bulk_import_users_with_legacy(import_data)


# Type mapping for external documentation
LEGACY_FIELD_MAPPING = {
    'is_member': {
        'legacy_type': 'boolean',
        'new_field': 'role',
        'new_type': 'string',
        'valid_values': [role.value for role in ProfileRole],
        'mapping_rules': {
            'True': 'registered_user',
            'False + has_email + org_domain': 'org_member', 
            'False + has_email': 'registered_user',
            'False + no_email': 'unregistered_user'
        }
    }
}


if __name__ == '__main__':
    # Example usage
    print("Legacy Role Shim - Example Usage")
    
    # Example export
    user_data = {
        'id': 1,
        'name': 'John Doe',
        'email': 'john@example.com',
        'role': 'registered_user'
    }
    
    exported = LegacyRoleShim.export_user_with_legacy_fields(user_data)
    print(f"Export: {user_data} → {exported}")
    
    # Example import
    legacy_data = {
        'id': 2,
        'name': 'Jane Smith', 
        'email': 'jane@example.com',
        'is_member': True
    }
    
    imported = LegacyRoleShim.import_user_with_legacy_fields(legacy_data)
    print(f"Import: {legacy_data} → {imported}")
    
    # Show field mapping documentation
    print(f"\nLegacy field mapping: {LEGACY_FIELD_MAPPING}")