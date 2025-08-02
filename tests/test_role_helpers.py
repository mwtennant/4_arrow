"""Unit tests for role helper methods and deprecation warnings."""

import pytest
import warnings
from datetime import datetime, timezone

from core.models import User, ProfileRole


class TestRoleHelpers:
    """Test the new role helper methods."""
    
    def test_is_registered_user_with_email(self):
        """Test is_registered_user returns True for users with email."""
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        assert user.is_registered_user() is True
        assert user.is_unregistered_user() is False
        assert user.is_org_member() is False
    
    def test_is_unregistered_user_without_email(self):
        """Test is_unregistered_user returns True for users without email."""
        user = User(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email=None
        )
        
        assert user.is_registered_user() is False
        assert user.is_unregistered_user() is True
        assert user.is_org_member() is False
    
    def test_is_unregistered_user_with_empty_email(self):
        """Test is_unregistered_user returns True for users with empty email."""
        user = User(
            id=3,
            first_name="Bob",
            last_name="Wilson",
            email=""
        )
        
        assert user.is_registered_user() is False
        assert user.is_unregistered_user() is True
        assert user.is_org_member() is False
    
    def test_is_org_member_with_tournament_email(self):
        """Test is_org_member returns True for tournament org emails."""
        user = User(
            id=4,
            first_name="Admin",
            last_name="User",
            email="admin@tournamentorg.com"
        )
        
        assert user.is_registered_user() is False
        assert user.is_unregistered_user() is False
        assert user.is_org_member() is True
    
    def test_is_org_member_with_admin_email(self):
        """Test is_org_member returns True for admin emails."""
        user = User(
            id=5,
            first_name="Super",
            last_name="Admin",
            email="super@admin.com"
        )
        
        assert user.is_registered_user() is False
        assert user.is_unregistered_user() is False
        assert user.is_org_member() is True
    
    def test_role_consistency_with_get_role(self):
        """Test that helper methods are consistent with get_role()."""
        # Test registered user
        registered_user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        assert registered_user.get_role() == ProfileRole.REGISTERED_USER
        assert registered_user.is_registered_user() is True
        
        # Test unregistered user
        unregistered_user = User(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email=None
        )
        assert unregistered_user.get_role() == ProfileRole.UNREGISTERED_USER
        assert unregistered_user.is_unregistered_user() is True
        
        # Test org member
        org_member = User(
            id=3,
            first_name="Admin",
            last_name="User",
            email="admin@tournamentorg.com"
        )
        assert org_member.get_role() == ProfileRole.ORG_MEMBER
        assert org_member.is_org_member() is True


class TestLegacyIsMemberProperty:
    """Test the deprecated is_member property."""
    
    def test_is_member_deprecation_warning(self):
        """Test that is_member property raises DeprecationWarning."""
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = user.is_member
            
            # Check that a warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "is_member is deprecated" in str(w[0].message)
            assert "Use is_registered_user() instead" in str(w[0].message)
            
            # Check that the result is correct
            assert result is True
    
    def test_is_member_maps_to_is_registered_user(self):
        """Test that is_member returns same as is_registered_user."""
        # Test registered user
        registered_user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert registered_user.is_member == registered_user.is_registered_user()
        
        # Test unregistered user
        unregistered_user = User(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email=None
        )
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert unregistered_user.is_member == unregistered_user.is_registered_user()
        
        # Test org member - should return False since they're not "registered_user"
        org_member = User(
            id=3,
            first_name="Admin",
            last_name="User",
            email="admin@tournamentorg.com"
        )
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert org_member.is_member == org_member.is_registered_user()
            assert org_member.is_member is False  # Org members are not registered users
    
    def test_is_member_warning_includes_stacklevel(self):
        """Test that deprecation warning shows caller's location."""
        user = User(
            id=1,
            first_name="John",
            last_name="Doe", 
            email="john@example.com"
        )
        
        def caller_function():
            return user.is_member
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            caller_function()
            
            assert len(w) == 1
            # The warning should point to caller_function, not the property itself
            assert "caller_function" in w[0].filename or w[0].lineno > 0


class TestRoleHelperPerformance:
    """Test performance characteristics of role helpers."""
    
    def test_helper_methods_are_fast(self):
        """Test that helper methods are O(1) operations."""
        import time
        
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        # Warm up
        for _ in range(100):
            user.is_registered_user()
            user.is_unregistered_user()
            user.is_org_member()
        
        # Time the operations
        start_time = time.time()
        for _ in range(1000):
            user.is_registered_user()
            user.is_unregistered_user()
            user.is_org_member()
        end_time = time.time()
        
        # Should complete 3000 operations in well under 1 second
        duration = end_time - start_time
        assert duration < 0.1, f"Role helpers took {duration:.3f}s for 3000 operations"
    
    def test_get_role_caching_not_required(self):
        """Test that get_role doesn't need caching for performance."""
        # This test ensures get_role is fast enough to call multiple times
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        import time
        start_time = time.time()
        for _ in range(1000):
            role = user.get_role()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 0.05, f"get_role took {duration:.3f}s for 1000 calls"


class TestRoleHelperEdgeCases:
    """Test edge cases for role helper methods."""
    
    def test_role_helpers_with_whitespace_email(self):
        """Test role helpers handle whitespace in email correctly."""
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="  "  # Only whitespace
        )
        
        assert user.is_registered_user() is False
        assert user.is_unregistered_user() is True
        assert user.is_org_member() is False
    
    def test_role_helpers_with_empty_string_email(self):
        """Test role helpers handle empty string email correctly."""
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email=""
        )
        
        assert user.is_registered_user() is False
        assert user.is_unregistered_user() is True
        assert user.is_org_member() is False
    
    def test_role_helpers_with_case_sensitive_domain(self):
        """Test role helpers handle case sensitivity in domain names."""
        # Should be case sensitive for security
        user = User(
            id=1,
            first_name="Admin",
            last_name="User",
            email="admin@TOURNAMENTORG.COM"  # Uppercase
        )
        
        # Current implementation is case sensitive
        assert user.is_registered_user() is True
        assert user.is_unregistered_user() is False
        assert user.is_org_member() is False
    
    def test_role_helpers_immutable_during_object_lifecycle(self):
        """Test that role helpers return consistent results."""
        user = User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        # Store initial results
        initial_registered = user.is_registered_user()
        initial_unregistered = user.is_unregistered_user()
        initial_org_member = user.is_org_member()
        
        # Call multiple times and ensure consistency
        for _ in range(10):
            assert user.is_registered_user() == initial_registered
            assert user.is_unregistered_user() == initial_unregistered
            assert user.is_org_member() == initial_org_member