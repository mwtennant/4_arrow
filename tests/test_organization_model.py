"""Tests for Organization model."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from core.models import Organization, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestOrganizationModel:
    """Test Organization model functionality."""
    
    def setup_method(self):
        """Set up test database."""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
        Base.metadata.drop_all(self.engine)
    
    def test_organization_creation_minimal(self):
        """Test creating organization with minimal required fields."""
        org = Organization(
            name="Test Organization"
        )
        
        assert org.name == "Test Organization"
        assert org.address is None
        assert org.phone is None
        assert org.email is None
        assert org.website is None
        assert org.deleted_at is None
        # created_at is set by database default, not in memory
    
    def test_organization_creation_full_data(self):
        """Test creating organization with all fields."""
        org = Organization(
            name="Pine Valley Lanes",
            address="123 Main Street, Anytown, ST 12345",
            phone="555-BOWL",
            email="info@pinevalley.com",
            website="https://pinevalley.com"
        )
        
        assert org.name == "Pine Valley Lanes"
        assert org.address == "123 Main Street, Anytown, ST 12345"
        assert org.phone == "555-BOWL"
        assert org.email == "info@pinevalley.com"
        assert org.website == "https://pinevalley.com"
        assert org.deleted_at is None
        # created_at is set by database default, not in memory
    
    def test_organization_database_persistence(self):
        """Test organization can be saved to and retrieved from database."""
        org = Organization(
            name="Database Test Org",
            address="456 Test Ave"
        )
        
        # Save to database
        self.session.add(org)
        self.session.commit()
        
        # Retrieve from database
        retrieved = self.session.query(Organization).filter_by(name="Database Test Org").first()
        
        assert retrieved is not None
        assert retrieved.name == "Database Test Org"
        assert retrieved.address == "456 Test Ave"
        assert retrieved.id is not None
    
    def test_organization_unique_name_constraint(self):
        """Test organization name uniqueness constraint."""
        # Create first organization
        org1 = Organization(name="Unique Test Org")
        self.session.add(org1)
        self.session.commit()
        
        # Try to create second organization with same name
        org2 = Organization(name="Unique Test Org")
        self.session.add(org2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            self.session.commit()
    
    def test_organization_soft_delete(self):
        """Test soft delete functionality."""
        org = Organization(name="Delete Test Org")
        
        # Initially not deleted
        assert not org.is_deleted()
        assert org.deleted_at is None
        
        # Soft delete
        with patch('sqlalchemy.sql.func.now') as mock_now:
            mock_time = datetime(2024, 1, 15, 10, 30, 0)
            mock_now.return_value = mock_time
            
            org.soft_delete()
            
            assert org.is_deleted()
            assert org.deleted_at == mock_time
    
    def test_organization_is_deleted_false_when_not_deleted(self):
        """Test is_deleted returns False when organization is not deleted."""
        org = Organization(name="Not Deleted Org")
        assert not org.is_deleted()
    
    def test_organization_is_deleted_true_when_deleted(self):
        """Test is_deleted returns True when organization is deleted."""
        org = Organization(name="Deleted Org")
        org.deleted_at = datetime.now()
        assert org.is_deleted()
    
    def test_organization_repr(self):
        """Test string representation of Organization."""
        org = Organization(name="Repr Test Org")
        org.id = 42
        
        repr_str = repr(org)
        assert "Organization" in repr_str
        assert "id=42" in repr_str
        assert "name='Repr Test Org'" in repr_str
    
    def test_organization_repr_without_id(self):
        """Test string representation without ID set."""
        org = Organization(name="No ID Org")
        
        repr_str = repr(org)
        assert "Organization" in repr_str
        assert "name='No ID Org'" in repr_str
        assert "id=None" in repr_str
    
    def test_organization_created_at_auto_set(self):
        """Test created_at is automatically set."""
        org = Organization(name="Timestamp Test Org")
        self.session.add(org)
        self.session.commit()
        
        assert org.created_at is not None
        assert isinstance(org.created_at, datetime)
    
    def test_organization_name_length_limits(self):
        """Test organization name length constraints."""
        # Test with exactly 255 characters (should work)
        long_name = "A" * 255
        org = Organization(name=long_name)
        self.session.add(org)
        self.session.commit()
        
        retrieved = self.session.query(Organization).filter_by(name=long_name).first()
        assert retrieved is not None
        assert len(retrieved.name) == 255
    
    def test_organization_website_length_limits(self):
        """Test organization website length constraints."""
        # Test with exactly 500 characters (should work)
        base_url = "https://example.com/"  # 19 characters
        long_website = base_url + "A" * (500 - len(base_url))  # Total 500 chars
        org = Organization(
            name="Website Test Org",
            website=long_website
        )
        self.session.add(org)
        self.session.commit()
        
        retrieved = self.session.query(Organization).filter_by(name="Website Test Org").first()
        assert retrieved is not None
        assert len(retrieved.website) == 500
    
    def test_organization_phone_format(self):
        """Test organization phone field accepts various formats."""
        phone_formats = [
            "555-1234",
            "(555) 123-4567",
            "555.123.4567",
            "+1-555-123-4567",
            "5551234567"
        ]
        
        for i, phone in enumerate(phone_formats):
            org = Organization(
                name=f"Phone Test Org {i}",
                phone=phone
            )
            self.session.add(org)
            self.session.commit()
            
            retrieved = self.session.query(Organization).filter_by(name=f"Phone Test Org {i}").first()
            assert retrieved.phone == phone
    
    def test_organization_email_format(self):
        """Test organization email field accepts various formats."""
        email_formats = [
            "simple@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
            "admin@bowling-center.org"
        ]
        
        for i, email in enumerate(email_formats):
            org = Organization(
                name=f"Email Test Org {i}",
                email=email
            )
            self.session.add(org)
            self.session.commit()
            
            retrieved = self.session.query(Organization).filter_by(name=f"Email Test Org {i}").first()
            assert retrieved.email == email
    
    def test_organization_website_format(self):
        """Test organization website field accepts various formats."""
        website_formats = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com",
            "https://subdomain.example.com",
            "https://example.com/path/to/page"
        ]
        
        for i, website in enumerate(website_formats):
            org = Organization(
                name=f"Website Test Org {i}",
                website=website
            )
            self.session.add(org)
            self.session.commit()
            
            retrieved = self.session.query(Organization).filter_by(name=f"Website Test Org {i}").first()
            assert retrieved.website == website
    
    def test_organization_tablename(self):
        """Test organization uses correct table name."""
        assert Organization.__tablename__ == 'organizations'
    
    def test_organization_nullable_fields(self):
        """Test which fields are nullable vs required."""
        # Only name should be required
        org = Organization(name="Required Field Test")
        
        # These should all be None by default (nullable)
        assert org.address is None
        assert org.phone is None
        assert org.email is None
        assert org.website is None
        assert org.deleted_at is None
        
        # Name should be set
        assert org.name == "Required Field Test"