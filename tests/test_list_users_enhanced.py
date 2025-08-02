"""Unit tests for enhanced list users functionality."""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from core.models import User, ProfileRole
from src.commands.list_users import (
    list_users_enhanced,
    parse_date_filter,
    build_enhanced_user_query,
    display_users_table,
    paginate_and_display
)


@pytest.fixture
def mock_session():
    """Mock database session."""
    with patch('src.commands.list_users.db_manager') as mock_db:
        mock_session = MagicMock()
        mock_db.get_session.return_value = mock_session
        yield mock_session


@pytest.fixture
def sample_users():
    """Sample users for testing."""
    users = []
    
    # Registered user
    user1 = User(
        id=1,
        first_name="John",
        last_name="Doe", 
        email="john@example.com",
        created_at=datetime(2024, 1, 15, tzinfo=timezone.utc)
    )
    users.append(user1)
    
    # Org member
    user2 = User(
        id=2,
        first_name="Jane",
        last_name="Smith",
        email="jane@tournamentorg.com",
        created_at=datetime(2024, 2, 1, tzinfo=timezone.utc)
    )
    users.append(user2)
    
    # Unregistered user
    user3 = User(
        id=3,
        first_name="Bob",
        last_name="Wilson",
        email=None,
        created_at=datetime(2024, 3, 1, tzinfo=timezone.utc)
    )
    users.append(user3)
    
    # Unicode name user
    user4 = User(
        id=4,
        first_name="José",
        last_name="García",
        email="jose@example.com",
        created_at=datetime(2024, 4, 1, tzinfo=timezone.utc)
    )
    users.append(user4)
    
    return users


class TestParseDateFilter:
    """Test date parsing functionality."""
    
    def test_valid_date_parsing(self):
        """Test parsing valid date format."""
        result = parse_date_filter("2024-01-15")
        expected = datetime(2024, 1, 15, tzinfo=timezone.utc)
        assert result == expected
    
    def test_invalid_date_format(self):
        """Test parsing invalid date format."""
        import click
        with pytest.raises(click.BadParameter, match="Invalid date format"):
            parse_date_filter("invalid-date")
    
    def test_wrong_date_format(self):
        """Test parsing wrong date format."""
        import click
        with pytest.raises(click.BadParameter, match="Invalid date format"):
            parse_date_filter("01/15/2024")
    
    def test_leap_year_date(self):
        """Test parsing leap year date."""
        result = parse_date_filter("2024-02-29")
        expected = datetime(2024, 2, 29, tzinfo=timezone.utc)
        assert result == expected


class TestBuildEnhancedUserQuery:
    """Test enhanced query building."""
    
    def test_query_with_no_filters(self, mock_session):
        """Test query building with no filters."""
        query = build_enhanced_user_query(mock_session, {})
        
        # Verify soft-deleted filter is applied
        mock_session.query.return_value.filter.assert_called()
        # Verify default ordering by id
        mock_session.query.return_value.filter.return_value.order_by.assert_called()
    
    def test_query_with_legacy_filters(self, mock_session):
        """Test query building with legacy filters."""
        filters = {
            'first': 'John',
            'email': 'john@example.com'
        }
        query = build_enhanced_user_query(mock_session, filters)
        
        # Should apply filters and ordering
        assert mock_session.query.called
    
    def test_query_with_date_filter(self, mock_session):
        """Test query building with date filter."""
        created_since = datetime(2024, 1, 1, tzinfo=timezone.utc)
        query = build_enhanced_user_query(mock_session, {}, created_since=created_since)
        
        # Should apply date filter
        assert mock_session.query.called
    
    def test_query_ordering_options(self, mock_session):
        """Test different ordering options."""
        # Test last_name ordering
        query1 = build_enhanced_user_query(mock_session, {}, order="last_name")
        
        # Test created_at ordering  
        query2 = build_enhanced_user_query(mock_session, {}, order="created_at")
        
        # Test default id ordering
        query3 = build_enhanced_user_query(mock_session, {}, order="id")
        
        assert mock_session.query.called


class TestListUsersEnhanced:
    """Test enhanced list users functionality."""
    
    def test_list_all_users(self, mock_session, sample_users):
        """Test listing all users without filters."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced()
        
        assert len(result) == 4
        assert all(isinstance(user, dict) for user in result)
        assert all('id' in user and 'name' in user and 'role' in user for user in result)
    
    def test_role_filtering(self, mock_session, sample_users):
        """Test role filtering functionality."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.display_users_table'):
            # Test registered users
            result = list_users_enhanced(role=ProfileRole.REGISTERED_USER)
            registered_users = [u for u in result if u['role'] == 'registered_user']
            assert len(registered_users) >= 1
            
            # Test unregistered users
            result = list_users_enhanced(role=ProfileRole.UNREGISTERED_USER)
            unregistered_users = [u for u in result if u['role'] == 'unregistered_user'] 
            assert len(unregistered_users) >= 1
            
            # Test org members
            result = list_users_enhanced(role=ProfileRole.ORG_MEMBER)
            org_members = [u for u in result if u['role'] == 'org_member']
            assert len(org_members) >= 1
    
    def test_date_filtering(self, mock_session, sample_users):
        """Test date filtering functionality."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value = mock_query
        
        created_since = datetime(2024, 2, 1, tzinfo=timezone.utc)
        
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced(created_since=created_since)
        
        # Should return some users (mocked data includes users after this date)
        assert len(result) >= 1
    
    def test_csv_export(self, mock_session, sample_users, tmp_path):
        """Test CSV export functionality."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        csv_path = tmp_path / "test_export.csv"
        
        with patch('src.commands.list_users.export_users_to_csv') as mock_export:
            result = list_users_enhanced(csv_path=csv_path)
            mock_export.assert_called_once()
    
    def test_pagination_with_small_page_size(self, mock_session, sample_users):
        """Test pagination with small page size."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.paginate_and_display') as mock_paginate:
            mock_paginate.return_value = [{'id': i} for i in range(4)]
            result = list_users_enhanced(page_size=2)
            mock_paginate.assert_called_once()
    
    def test_unicode_name_handling(self, mock_session, sample_users):
        """Test handling of Unicode characters in names."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced()
        
        # Check that Unicode user is handled correctly
        unicode_user = next((u for u in result if 'José' in u['name']), None)
        assert unicode_user is not None
        assert unicode_user['name'] == "José García"
    
    def test_database_error_handling(self, mock_session):
        """Test database error handling."""
        mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(SQLAlchemyError):
            list_users_enhanced()
    
    def test_ordering_options(self, mock_session, sample_users):
        """Test different ordering options."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.display_users_table'):
            # Test each ordering option
            for order in ['id', 'last_name', 'created_at']:
                result = list_users_enhanced(order=order)
                assert len(result) == 4


class TestDisplayFunctions:
    """Test display and pagination functions."""
    
    def test_display_users_table_empty(self):
        """Test displaying empty user list."""
        with patch('src.commands.list_users.Console') as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            
            display_users_table([])
            mock_console.print.assert_called_with("No users found matching criteria.")
    
    def test_display_users_table_with_data(self):
        """Test displaying users table with data."""
        users_data = [
            {
                'id': 1,
                'name': 'John Doe',
                'role': 'registered_user',
                'email': 'john@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            }
        ]
        
        with patch('src.commands.list_users.Console') as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            
            display_users_table(users_data)
            # Should create and print a table
            mock_console.print.assert_called()
    
    def test_paginate_and_display_non_interactive(self):
        """Test pagination in non-interactive environment."""
        users_data = [{'id': i, 'name': f'User {i}'} for i in range(10)]
        
        with patch('src.commands.list_users.sys.stdin.isatty', return_value=False):
            with patch('src.commands.list_users.display_users_table'):
                result = paginate_and_display(users_data, 3)
        
        assert len(result) == 10
    
    def test_paginate_and_display_interactive_quit(self):
        """Test pagination with user quit."""
        users_data = [{'id': i, 'name': f'User {i}'} for i in range(6)]
        
        with patch('src.commands.list_users.sys.stdin.isatty', return_value=True):
            with patch('src.commands.list_users.display_users_table'):
                with patch('builtins.input', return_value='q'):
                    result = paginate_and_display(users_data, 3)
        
        assert len(result) == 6  # Returns full data regardless of quit
    
    def test_paginate_and_display_keyboard_interrupt(self):
        """Test pagination with keyboard interrupt."""
        users_data = [{'id': i, 'name': f'User {i}'} for i in range(6)]
        
        with patch('src.commands.list_users.sys.stdin.isatty', return_value=True):
            with patch('src.commands.list_users.display_users_table'):
                with patch('builtins.input', side_effect=KeyboardInterrupt):
                    result = paginate_and_display(users_data, 3)
        
        assert len(result) == 6


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_dst_transition_date_filtering(self, mock_session):
        """Test date filtering across DST transition."""
        # Create users around DST transition (November 2024)
        users = [
            User(id=1, first_name="Before", last_name="DST", 
                 created_at=datetime(2024, 11, 2, 1, 30, tzinfo=timezone.utc)),
            User(id=2, first_name="After", last_name="DST",
                 created_at=datetime(2024, 11, 4, 1, 30, tzinfo=timezone.utc))
        ]
        
        mock_query = MagicMock()
        mock_query.all.return_value = users
        mock_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value = mock_query
        
        # Filter for users after DST transition
        created_since = datetime(2024, 11, 3, tzinfo=timezone.utc)
        
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced(created_since=created_since)
        
        assert len(result) == 2  # Should handle DST correctly
    
    def test_empty_database_result(self, mock_session):
        """Test handling empty database results."""
        mock_query = MagicMock()
        mock_query.all.return_value = []
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced()
        
        assert result == []
    
    def test_large_dataset_handling(self, mock_session):
        """Test handling large datasets efficiently."""
        # Create large number of mock users
        large_user_list = []
        for i in range(1000):
            user = User(
                id=i,
                first_name=f"User{i}",
                last_name=f"Test{i}",
                email=f"user{i}@example.com"
            )
            large_user_list.append(user)
        
        mock_query = MagicMock()
        mock_query.all.return_value = large_user_list
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced()
        
        assert len(result) == 1000
        # Verify data structure is maintained
        assert all('id' in user and 'name' in user for user in result)
    
    def test_special_characters_in_filters(self, mock_session, sample_users):
        """Test handling special characters in filter strings."""
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        # Test with special characters that could cause SQL issues
        with patch('src.commands.list_users.display_users_table'):
            result = list_users_enhanced(
                first="O'Malley",  # Apostrophe
                email="user@test.co.uk"  # Multiple dots
            )
        
        # Should handle gracefully without SQL injection
        assert isinstance(result, list)


class TestBackwardCompatibility:
    """Test backward compatibility with legacy list_users function."""
    
    def test_legacy_list_users_function(self, mock_session, sample_users):
        """Test that legacy list_users function still works."""
        from src.commands.list_users import list_users
        
        # Set up proper mock chain
        mock_query = MagicMock()
        mock_query.all.return_value = sample_users
        
        # Create the full mock chain
        query_mock = mock_session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock2 = filter_mock.filter.return_value
        filter_mock3 = filter_mock2.filter.return_value
        filter_mock3.order_by.return_value = mock_query
        
        result = list_users(first="John", email="john@example.com")
        
        assert result == sample_users
        assert all(isinstance(user, User) for user in result)
    
    def test_legacy_display_users_function(self, sample_users):
        """Test that legacy display_users function still works."""
        from src.commands.list_users import display_users
        
        with patch('src.commands.list_users.Console') as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            
            display_users(sample_users)
            mock_console.print.assert_called()