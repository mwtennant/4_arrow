"""Tests for the list users command."""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from src.commands.list_users import list_users, build_user_query, display_users
from core.models import User


class TestListUsers:
    """Test cases for the list_users function."""

    def test_list_users_no_filters(self):
        """Test listing all users when no filters are applied."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            # Mock users
            mock_users = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com"),
                User(id=2, first_name="Jane", last_name="Smith", email="jane@example.com")
            ]
            mock_session.query.return_value.all.return_value = mock_users
            
            result = list_users()
            
            assert len(result) == 2
            assert result[0].first_name == "John"
            assert result[1].first_name == "Jane"
            mock_session.query.assert_called_once_with(User)

    def test_list_users_with_first_name_filter(self):
        """Test listing users with first name filter."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            # Mock query chain
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com")
            ]
            
            result = list_users(first="John")
            
            assert len(result) == 1
            assert result[0].first_name == "John"
            mock_session.query.assert_called_once_with(User)

    def test_list_users_with_last_name_filter(self):
        """Test listing users with last name filter."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com")
            ]
            
            result = list_users(last="Doe")
            
            assert len(result) == 1
            assert result[0].last_name == "Doe"

    def test_list_users_with_email_filter(self):
        """Test listing users with email filter."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com")
            ]
            
            result = list_users(email="john@example.com")
            
            assert len(result) == 1
            assert result[0].email == "john@example.com"

    def test_list_users_with_phone_filter(self):
        """Test listing users with phone filter."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", phone="555-1234")
            ]
            
            result = list_users(phone="555-1234")
            
            assert len(result) == 1
            assert result[0].phone == "555-1234"

    def test_list_users_with_address_filter(self):
        """Test listing users with address filter."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", address="123 Main St")
            ]
            
            result = list_users(address="123 Main St")
            
            assert len(result) == 1
            assert result[0].address == "123 Main St"

    def test_list_users_with_usbc_id_filter(self):
        """Test listing users with USBC ID filter (exact match)."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", usbc_id="12345")
            ]
            
            result = list_users(usbc_id="12345")
            
            assert len(result) == 1
            assert result[0].usbc_id == "12345"

    def test_list_users_with_tnba_id_filter(self):
        """Test listing users with TNBA ID filter (exact match)."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", tnba_id="67890")
            ]
            
            result = list_users(tnba_id="67890")
            
            assert len(result) == 1
            assert result[0].tnba_id == "67890"

    def test_list_users_with_multiple_filters(self):
        """Test listing users with multiple filters (AND logic)."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com")
            ]
            
            result = list_users(first="John", email="john@example.com")
            
            assert len(result) == 1
            assert result[0].first_name == "John"
            assert result[0].email == "john@example.com"

    def test_list_users_with_all_filters(self):
        """Test listing users with all filters applied."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(
                    id=1,
                    first_name="John",
                    last_name="Doe",
                    email="john@example.com",
                    phone="555-1234",
                    address="123 Main St",
                    usbc_id="12345",
                    tnba_id="67890"
                )
            ]
            
            result = list_users(
                first="John",
                last="Doe",
                email="john@example.com",
                phone="555-1234",
                address="123 Main St",
                usbc_id="12345",
                tnba_id="67890"
            )
            
            assert len(result) == 1
            assert result[0].first_name == "John"
            assert result[0].last_name == "Doe"

    def test_list_users_empty_result(self):
        """Test listing users when no users match the filter (Edge Case)."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = []
            
            result = list_users(first="NonExistent")
            
            assert len(result) == 0

    def test_list_users_database_error(self):
        """Test listing users when database connection fails."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.side_effect = SQLAlchemyError("Database connection failed")
            
            with pytest.raises(SQLAlchemyError):
                list_users()

    def test_list_users_ignores_empty_filters(self):
        """Test that empty string filters are ignored."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_users = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com")
            ]
            mock_session.query.return_value.all.return_value = mock_users
            
            result = list_users(first="", last="   ", email=None)
            
            assert len(result) == 1
            # Should not apply any filters, so query should just return all users
            mock_session.query.assert_called_once_with(User)

    def test_list_users_strips_whitespace(self):
        """Test that filters strip whitespace correctly."""
        with patch('src.commands.list_users.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                User(id=1, first_name="John", last_name="Doe", email="john@example.com")
            ]
            
            result = list_users(first="  John  ", last="  Doe  ")
            
            assert len(result) == 1
            # The function should strip whitespace and use "John" and "Doe" as filters


class TestBuildUserQuery:
    """Test cases for the build_user_query function."""

    def test_build_user_query_no_filters(self):
        """Test building query with no filters."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        
        result = build_user_query(mock_session, {})
        
        assert result == mock_query
        mock_session.query.assert_called_once_with(User)

    def test_build_user_query_with_partial_match_filters(self):
        """Test building query with partial match filters."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        filters = {
            'first': 'John',
            'last': 'Doe',
            'email': 'john@example.com',
            'phone': '555',
            'address': 'Main St'
        }
        
        build_user_query(mock_session, filters)
        
        # Should call filter 5 times (once for each partial match filter)
        assert mock_query.filter.call_count == 5

    def test_build_user_query_with_exact_match_filters(self):
        """Test building query with exact match filters."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        filters = {
            'usbc_id': '12345',
            'tnba_id': '67890'
        }
        
        build_user_query(mock_session, filters)
        
        # Should call filter 2 times (once for each exact match filter)
        assert mock_query.filter.call_count == 2

    def test_build_user_query_with_mixed_filters(self):
        """Test building query with both partial and exact match filters."""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        filters = {
            'first': 'John',
            'usbc_id': '12345',
            'email': 'john@example.com',
            'tnba_id': '67890'
        }
        
        build_user_query(mock_session, filters)
        
        # Should call filter 4 times (for all 4 filters)
        assert mock_query.filter.call_count == 4


class TestDisplayUsers:
    """Test cases for the display_users function."""

    @patch('src.commands.list_users.Console')
    def test_display_users_empty_list(self, mock_console_class):
        """Test displaying empty user list."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        display_users([])
        
        mock_console.print.assert_called_once_with("No users found matching criteria.")

    @patch('src.commands.list_users.Console')
    @patch('src.commands.list_users.Table')
    def test_display_users_with_users(self, mock_table_class, mock_console_class):
        """Test displaying users in table format."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table
        
        users = [
            User(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="555-1234",
                address="123 Main St",
                usbc_id="12345",
                tnba_id="67890"
            ),
            User(
                id=2,
                first_name="Jane",
                last_name="Smith",
                email=None,
                phone=None,
                address=None,
                usbc_id=None,
                tnba_id=None
            )
        ]
        
        display_users(users)
        
        # Should create table with proper configuration
        mock_table_class.assert_called_once_with(show_header=True, header_style="bold", border_style="dim")
        
        # Should add 8 columns
        assert mock_table.add_column.call_count == 8
        
        # Should add 2 rows (one for each user)
        assert mock_table.add_row.call_count == 2
        
        # Should print the table
        mock_console.print.assert_called_once_with(mock_table)

    @patch('src.commands.list_users.Console')
    @patch('src.commands.list_users.Table')
    def test_display_users_handles_none_values(self, mock_table_class, mock_console_class):
        """Test displaying users with None values properly handled."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table
        
        users = [
            User(
                id=1,
                first_name="John",
                last_name="Doe",
                email=None,
                phone=None,
                address=None,
                usbc_id=None,
                tnba_id=None
            )
        ]
        
        display_users(users)
        
        # Should add one row with empty strings for None values
        mock_table.add_row.assert_called_once_with(
            "1",  # user.id as string
            "John",  # user.first_name
            "Doe",  # user.last_name
            "",  # user.email or ""
            "",  # user.phone or ""
            "",  # user.address or ""
            "",  # user.usbc_id or ""
            ""   # user.tnba_id or ""
        )