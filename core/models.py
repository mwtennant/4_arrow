"""User and Organization models for the 4th Arrow Tournament Control application."""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import declarative_base, relationship
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
    
    # Relationships
    organization_memberships = relationship("OrganizationMembership", back_populates="user", cascade="all, delete-orphan")
    
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
    
    def get_organization_roles(self, organization_id: int) -> List['Role']:
        """Get user's roles for a specific organization.
        
        Args:
            organization_id: The ID of the organization
            
        Returns:
            List of roles the user has in the specified organization
        """
        membership = next((m for m in self.organization_memberships if m.organization_id == organization_id), None)
        return [membership.role] if membership and membership.role else []
    
    def has_permission(self, permission_name: str, organization_id: int) -> bool:
        """Check if user has a specific permission in an organization.
        
        Args:
            permission_name: Name of the permission to check
            organization_id: The ID of the organization
            
        Returns:
            True if user has the specified permission in the organization
        """
        roles = self.get_organization_roles(organization_id)
        for role in roles:
            for role_perm in role.role_permissions:
                if role_perm.permission.name.lower() == permission_name.lower():
                    return True
        return False
    
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
    
    # Relationships
    permissions = relationship("Permission", back_populates="organization", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="organization", cascade="all, delete-orphan")
    memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    
    def soft_delete(self) -> None:
        """Soft delete the organization by setting deleted_at timestamp."""
        self.deleted_at = func.now()
    
    def is_deleted(self) -> bool:
        """Check if the organization is soft-deleted."""
        return self.deleted_at is not None
    
    def get_members(self) -> List['User']:
        """Get all users who are members of this organization.
        
        Returns:
            List of User objects who are members of this organization
        """
        return [membership.user for membership in self.memberships]
    
    def get_member_count(self) -> int:
        """Get count of organization members.
        
        Returns:
            Number of members in the organization
        """
        return len(self.memberships)
    
    def __repr__(self) -> str:
        """String representation of Organization model."""
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Permission(Base):
    """Permission model for organization-scoped access rights."""
    
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="permissions")
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'organization_id', name='uq_permission_name_org'),
        Index('ix_permission_org_name', 'organization_id', 'name'),
    )
    
    def __repr__(self) -> str:
        """String representation of Permission model."""
        return f"<Permission(id={self.id}, name='{self.name}', organization_id={self.organization_id})>"


class Role(Base):
    """Role model for organization-scoped user roles."""
    
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)  # Future hierarchy
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="roles")
    parent_role = relationship("Role", remote_side=[id], back_populates="child_roles")
    child_roles = relationship("Role", back_populates="parent_role")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    memberships = relationship("OrganizationMembership", back_populates="role")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'organization_id', name='uq_role_name_org'),
        Index('ix_role_org_name', 'organization_id', 'name'),
    )
    
    def __repr__(self) -> str:
        """String representation of Role model."""
        return f"<Role(id={self.id}, name='{self.name}', organization_id={self.organization_id})>"


class RolePermission(Base):
    """Association table for Role-Permission many-to-many relationship."""
    
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
        Index('ix_role_permission_role', 'role_id'),
        Index('ix_role_permission_permission', 'permission_id'),
    )
    
    def __repr__(self) -> str:
        """String representation of RolePermission model."""
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>"


class OrganizationMembership(Base):
    """Association table for User-Organization membership with roles."""
    
    __tablename__ = 'organization_memberships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="organization_memberships")
    organization = relationship("Organization", back_populates="memberships")
    role = relationship("Role", back_populates="memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
        Index('ix_membership_user', 'user_id'),
        Index('ix_membership_org', 'organization_id'),
        Index('ix_membership_role', 'role_id'),
    )
    
    @property
    def is_registered(self) -> bool:
        """Determine registration status based on user's email/password.
        
        Returns:
            True if the user is registered (has email)
        """
        return bool(self.user.email and self.user.email.strip())
    
    def __repr__(self) -> str:
        """String representation of OrganizationMembership model."""
        return f"<OrganizationMembership(id={self.id}, user_id={self.user_id}, organization_id={self.organization_id})>"