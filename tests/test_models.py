"""Tests for User model."""

import pytest
from datetime import datetime

from core.models import User, Base
from storage.database import DatabaseManager


class TestUserModel:
    """Test cases for User model."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a test database manager."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.create_tables()
        return db_manager
    
    @pytest.fixture
    def session(self, db_manager):
        """Create a test database session."""
        session = db_manager.get_session()
        yield session
        session.close()
    
    def test_user_creation(self, session):
        """Test creating a user with all fields."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone="555-1234",
            address="123 Main St",
            usbc_id="12345",
            tnba_id="67890"
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone == "555-1234"
        assert user.address == "123 Main St"
        assert user.usbc_id == "12345"
        assert user.tnba_id == "67890"
        assert isinstance(user.created_at, datetime)
    
    def test_user_creation_required_fields_only(self, session):
        """Test creating a user with only required fields."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone == "555-1234"
        assert user.address is None
        assert user.usbc_id is None
        assert user.tnba_id is None
        assert isinstance(user.created_at, datetime)
    
    def test_user_repr(self, session):
        """Test User string representation."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        expected = f"<User(id={user.id}, email='test@example.com', name='John Doe')>"
        assert str(user) == expected
    
    def test_unique_email_constraint(self, session):
        """Test that email must be unique."""
        user1 = User(
            email="test@example.com",
            password_hash="hashed_password1",
            first_name="John",
            last_name="Doe",
            phone="555-1234"
        )
        
        user2 = User(
            email="test@example.com",
            password_hash="hashed_password2",
            first_name="Jane",
            last_name="Smith",
            phone="555-5678"
        )
        
        session.add(user1)
        session.commit()
        
        session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()