"""Tests for the create user command."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.commands.create import create_user, validate_create_args
from core.models import User


class TestCreateUser:
    """Test cases for the create_user function."""

    def test_create_user_with_required_args_only(self):
        """Test creating a user with only required arguments."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            
            user = create_user(first="Bob", last="Lane")
            
            assert user.first_name == "Bob"
            assert user.last_name == "Lane"
            assert user.email is None
            assert user.phone is None
            assert user.address is None
            assert user.usbc_id is None
            assert user.tnba_id is None
            assert user.is_unregistered_user() is True
            
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_create_user_with_all_args(self):
        """Test creating a user with all arguments provided."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            
            user = create_user(
                first="Alice",
                last="Smith",
                email="alice@example.com",
                phone="555-1234",
                address="123 Main St",
                usbc_id="12345",
                tnba_id="67890"
            )
            
            assert user.first_name == "Alice"
            assert user.last_name == "Smith"
            assert user.email == "alice@example.com"
            assert user.phone == "555-1234"
            assert user.address == "123 Main St"
            assert user.usbc_id == "12345"
            assert user.tnba_id == "67890"
            assert user.is_registered_user() is True
            
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_create_user_with_no_email(self):
        """Test creating a non-member user without email."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            
            user = create_user(
                first="John",
                last="Doe",
                phone="555-5678",
                address="456 Oak Ave"
            )
            
            assert user.first_name == "John"
            assert user.last_name == "Doe"
            assert user.email is None
            assert user.phone == "555-5678"
            assert user.address == "456 Oak Ave"
            assert user.is_unregistered_user() is True
            
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_duplicate_email_returns_error(self):
        """Test that duplicate email raises IntegrityError."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            # Mock existing user with same email
            existing_user = User(email="alice@example.com")
            mock_session.query.return_value.filter_by.return_value.first.return_value = existing_user
            
            with pytest.raises(IntegrityError) as exc_info:
                create_user(
                    first="Alice",
                    last="Smith",
                    email="alice@example.com"
                )
            
            assert "Email already exists" in str(exc_info.value)

    def test_duplicate_usbc_id_returns_error(self):
        """Test that duplicate USBC ID raises IntegrityError."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            # Mock no email conflict but USBC ID conflict
            def mock_filter_by(email=None, usbc_id=None, tnba_id=None):
                if email:
                    return MagicMock(first=MagicMock(return_value=None))
                if usbc_id:
                    return MagicMock(first=MagicMock(return_value=User(usbc_id=usbc_id)))
                return MagicMock(first=MagicMock(return_value=None))
            
            mock_session.query.return_value.filter_by.side_effect = mock_filter_by
            
            with pytest.raises(IntegrityError) as exc_info:
                create_user(
                    first="Bob",
                    last="Lane",
                    usbc_id="12345"
                )
            
            assert "USBC ID already exists" in str(exc_info.value)

    def test_duplicate_tnba_id_returns_error(self):
        """Test that duplicate TNBA ID raises IntegrityError."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            
            # Mock no email/usbc conflict but TNBA ID conflict
            def mock_filter_by(email=None, usbc_id=None, tnba_id=None):
                if email or usbc_id:
                    return MagicMock(first=MagicMock(return_value=None))
                if tnba_id:
                    return MagicMock(first=MagicMock(return_value=User(tnba_id=tnba_id)))
                return MagicMock(first=MagicMock(return_value=None))
            
            mock_session.query.return_value.filter_by.side_effect = mock_filter_by
            
            with pytest.raises(IntegrityError) as exc_info:
                create_user(
                    first="Charlie",
                    last="Brown",
                    tnba_id="67890"
                )
            
            assert "TNBA ID already exists" in str(exc_info.value)

    def test_empty_first_name_returns_error(self):
        """Test that empty first name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_user(first="", last="Smith")
        
        assert "First name cannot be empty" in str(exc_info.value)

    def test_empty_last_name_returns_error(self):
        """Test that empty last name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_user(first="John", last="")
        
        assert "Last name cannot be empty" in str(exc_info.value)

    def test_whitespace_only_first_name_returns_error(self):
        """Test that whitespace-only first name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_user(first="   ", last="Smith")
        
        assert "First name cannot be empty" in str(exc_info.value)

    def test_whitespace_only_last_name_returns_error(self):
        """Test that whitespace-only last name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_user(first="John", last="   ")
        
        assert "Last name cannot be empty" in str(exc_info.value)

    def test_string_fields_are_trimmed(self):
        """Test that string fields are properly trimmed."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            
            user = create_user(
                first="  Alice  ",
                last="  Smith  ",
                email="  alice@example.com  ",
                phone="  555-1234  ",
                address="  123 Main St  ",
                usbc_id="  12345  ",
                tnba_id="  67890  "
            )
            
            assert user.first_name == "Alice"
            assert user.last_name == "Smith"
            assert user.email == "alice@example.com"
            assert user.phone == "555-1234"
            assert user.address == "123 Main St"
            assert user.usbc_id == "12345"
            assert user.tnba_id == "67890"

    def test_database_error_handling(self):
        """Test handling of database errors."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            mock_session.commit.side_effect = SQLAlchemyError("Database connection failed")
            
            with pytest.raises(SQLAlchemyError):
                create_user(first="John", last="Doe")
            
            mock_session.rollback.assert_called_once()

    def test_session_is_closed_on_success(self):
        """Test that database session is properly closed on success."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            
            create_user(first="John", last="Doe")
            
            mock_session.close.assert_called_once()

    def test_session_is_closed_on_error(self):
        """Test that database session is properly closed on error."""
        with patch('src.commands.create.db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            mock_session.commit.side_effect = SQLAlchemyError("Database error")
            
            with pytest.raises(SQLAlchemyError):
                create_user(first="John", last="Doe")
            
            mock_session.close.assert_called_once()


class TestValidateCreateArgs:
    """Test cases for the validate_create_args function."""

    def test_validate_create_args_with_valid_inputs(self):
        """Test validation with valid inputs."""
        # Should not raise any exception
        validate_create_args("John", "Doe")

    def test_validate_create_args_empty_first_name(self):
        """Test validation with empty first name exits with code 3."""
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print') as mock_print:
                validate_create_args("", "Doe")
                
                mock_print.assert_called_with("ERROR: First name cannot be empty", file=sys.stderr)
                mock_exit.assert_called_with(3)

    def test_validate_create_args_empty_last_name(self):
        """Test validation with empty last name exits with code 3."""
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print') as mock_print:
                validate_create_args("John", "")
                
                mock_print.assert_called_with("ERROR: Last name cannot be empty", file=sys.stderr)
                mock_exit.assert_called_with(3)

    def test_validate_create_args_whitespace_first_name(self):
        """Test validation with whitespace-only first name exits with code 3."""
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print') as mock_print:
                validate_create_args("   ", "Doe")
                
                mock_print.assert_called_with("ERROR: First name cannot be empty", file=sys.stderr)
                mock_exit.assert_called_with(3)

    def test_validate_create_args_whitespace_last_name(self):
        """Test validation with whitespace-only last name exits with code 3."""
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print') as mock_print:
                validate_create_args("John", "   ")
                
                mock_print.assert_called_with("ERROR: Last name cannot be empty", file=sys.stderr)
                mock_exit.assert_called_with(3)