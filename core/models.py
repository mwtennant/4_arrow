"""User and Organization models for the 4th Arrow Tournament Control application."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ProfileRole(Enum):
    """User profile role classification."""
    REGISTERED_USER = "registered_user"
    UNREGISTERED_USER = "unregistered_user"  
    ORG_MEMBER = "org_member"


class User(Base):
    """User model for storing user account information."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(Text, nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    usbc_id = Column(String(50), nullable=True)
    tnba_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self) -> None:
        """Soft delete the user by setting deleted_at timestamp."""
        self.deleted_at = func.now()
    
    def is_deleted(self) -> bool:
        """Check if the user is soft-deleted."""
        return self.deleted_at is not None
    
    def get_role(self) -> ProfileRole:
        """Classify user role based on profile completeness and organization membership.
        
        Returns:
            ProfileRole: The user's role classification
        """
        # For now, we'll implement basic logic. In future phases, org_member
        # would check for actual organization membership
        if self.email and self.email.strip():
            # Users with tournament org emails or admin privileges would be org_member
            if (self.email.endswith('@tournamentorg.com') or 
                self.email.endswith('@admin.com')):
                return ProfileRole.ORG_MEMBER
            return ProfileRole.REGISTERED_USER
        else:
            return ProfileRole.UNREGISTERED_USER
    
    def is_registered_user(self) -> bool:
        """Check if user is a registered user (has email).
        
        Returns:
            bool: True if user has email and can authenticate
        """
        return self.get_role() == ProfileRole.REGISTERED_USER
    
    def is_unregistered_user(self) -> bool:
        """Check if user is unregistered (no email).
        
        Returns:
            bool: True if user has no email (tournament-only profile)
        """
        return self.get_role() == ProfileRole.UNREGISTERED_USER
    
    def is_org_member(self) -> bool:
        """Check if user is an organization member.
        
        Returns:
            bool: True if user has organizational privileges
        """
        return self.get_role() == ProfileRole.ORG_MEMBER
    
    @property
    def is_member(self) -> bool:
        """Legacy property for backward compatibility.
        
        Deprecated: Use is_registered_user() instead.
        
        Returns:
            bool: True if user is registered (legacy equivalent)
        """
        import warnings
        warnings.warn(
            "is_member is deprecated. Use is_registered_user() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.is_registered_user()
    
    def __repr__(self) -> str:
        """String representation of User model."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"


class Organization(Base):
    """Organization model for storing tournament organization information."""
    
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self) -> None:
        """Soft delete the organization by setting deleted_at timestamp."""
        self.deleted_at = func.now()
    
    def is_deleted(self) -> bool:
        """Check if the organization is soft-deleted."""
        return self.deleted_at is not None
    
    def __repr__(self) -> str:
        """String representation of Organization model."""
        return f"<Organization(id={self.id}, name='{self.name}')>"