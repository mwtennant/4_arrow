# Product Requirements Prompt: Add Organization Data Models (Phase Org-C)

## Summary

Implement core database models to support organization membership, roles, permissions, and their relationships for the 4th Arrow Tournament Control application. This feature establishes the foundational data structures that enable multi-organization management with proper user roles and permissions, creating the framework for comprehensive organization functionality including member management, role assignments, and permission-based access controls.

## Step-by-Step Plan

### Slice 1: Core Model Implementation

1. Add `Permission` model to `core/models.py` with organization-scoped unique names
2. Add `Role` model to `core/models.py` with organization-scoped unique names and future hierarchy support
3. Add `RolePermission` association model for many-to-many role-permission mapping
4. Add `OrganizationMembership` model to link users to organizations with roles

### Slice 2: Database Integration and Migration

1. Create SQLAlchemy migration script for the four new tables
2. Apply necessary indices and constraints (unique combinations, foreign keys)
3. Update database initialization logic in `storage/database.py`
4. Ensure proper relationship mappings and cascade behaviors

### Slice 3: Validation and Testing

1. Write comprehensive test suite covering all model relationships
2. Test unique constraints (case-insensitive name validation)
3. Test foreign key constraints and cascade behaviors
4. Ensure 90% test coverage as specified in requirements
5. Test role-permission resolution and membership management

## File List

### Core Implementation Files

- `core/models.py` - Add four new SQLAlchemy models (Permission, Role, RolePermission, OrganizationMembership)
- `storage/database.py` - Update database initialization (reference existing patterns)

### Migration Files

- `migrations/add_organization_models.py` - SQLAlchemy migration script for new tables

### Test Files

- `tests/test_organization_membership_models.py` - Unit tests for new organization models
- `tests/test_models.py` - Extend existing model tests with new relationships
- `tests/test_migration.py` - Migration script tests

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy) - existing

## Database Schema

### New Tables and Models

#### Permission Model
```python
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
```

#### Role Model
```python
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
```

#### RolePermission Model
```python
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
```

#### OrganizationMembership Model
```python
class OrganizationMembership(Base):
    """Association table for User-Organization membership with roles."""
    
    __tablename__ = 'organization_memberships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    is_registered = Column(Boolean, nullable=False, default=False)
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
        """Determine registration status based on user's email/password."""
        return bool(self.user.email and self.user.email.strip())
```

### Updated Models

#### User Model Extensions
```python
# Add to existing User model
organization_memberships = relationship("OrganizationMembership", back_populates="user", cascade="all, delete-orphan")

def get_organization_roles(self, organization_id: int) -> List[Role]:
    """Get user's roles for a specific organization."""
    membership = next((m for m in self.organization_memberships if m.organization_id == organization_id), None)
    return [membership.role] if membership and membership.role else []

def has_permission(self, permission_name: str, organization_id: int) -> bool:
    """Check if user has a specific permission in an organization."""
    roles = self.get_organization_roles(organization_id)
    for role in roles:
        for role_perm in role.role_permissions:
            if role_perm.permission.name.lower() == permission_name.lower():
                return True
    return False
```

#### Organization Model Extensions
```python
# Add to existing Organization model
permissions = relationship("Permission", back_populates="organization", cascade="all, delete-orphan")
roles = relationship("Role", back_populates="organization", cascade="all, delete-orphan")
memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")

def get_members(self) -> List[User]:
    """Get all users who are members of this organization."""
    return [membership.user for membership in self.memberships]

def get_member_count(self) -> int:
    """Get count of organization members."""
    return len(self.memberships)
```

## Validations

### pytest Test Coverage

- **Permission model tests**:
  - ✅ Create permission with valid organization reference
  - ✅ Permission name uniqueness within organization (case-insensitive)
  - 🚫 Permission name duplication within same organization fails
  - ✅ Permission name can be duplicated across different organizations
  - ✅ Permission description handling (optional field)
  - ✅ Permission cascade deletion with organization

- **Role model tests**:
  - ✅ Create role with valid organization reference
  - ✅ Role name uniqueness within organization (case-insensitive)
  - 🚫 Role name duplication within same organization fails
  - ✅ Role name can be duplicated across different organizations
  - ✅ Role hierarchy support (parent_role_id handling)
  - ✅ Role cascade deletion with organization

- **RolePermission model tests**:
  - ✅ Create role-permission association
  - 🚫 Duplicate role-permission associations fail
  - ✅ Cascade deletion when role or permission is deleted
  - ✅ Role-permission resolution works correctly
  - ✅ Many-to-many relationship integrity

- **OrganizationMembership model tests**:
  - ✅ Create membership with valid user and organization
  - 🚫 Duplicate user-organization memberships fail
  - ✅ Membership with and without role assignment
  - ✅ is_registered property based on user email/password
  - ✅ Cascade deletion behavior
  - 🚫 Invalid role ID assignment fails FK constraint

### Coverage Requirements

- Minimum 90% coverage as specified in feature requirements
- All unique constraints tested (both success and failure cases)
- All foreign key constraints tested
- All relationship mappings verified
- Edge cases covered in tests

## Technical Specifications

### Implementation Requirements

- Code location: `core/models.py` (extend existing file)
- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing SQLAlchemy Base and database layer
- Implement case-insensitive name uniqueness for permissions and roles
- Proper foreign key relationships and cascade behaviors

### Database Constraints

- **Unique Constraints**:
  - Permission: (lower(name), organization_id)
  - Role: (lower(name), organization_id)
  - RolePermission: (role_id, permission_id)
  - OrganizationMembership: (user_id, organization_id)

- **Foreign Key Constraints**:
  - Permission.organization_id → organizations.id
  - Role.organization_id → organizations.id
  - Role.parent_role_id → roles.id (self-reference)
  - RolePermission.role_id → roles.id
  - RolePermission.permission_id → permissions.id
  - OrganizationMembership.user_id → users.id
  - OrganizationMembership.organization_id → organizations.id
  - OrganizationMembership.role_id → roles.id

- **Indices**:
  - Performance optimization for common queries
  - Organization-scoped name lookups
  - Membership and role resolution queries

## References to Examples/Docs

### External Documentation

- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html) - Model relationships and associations
- [SQLAlchemy Constraints](https://docs.sqlalchemy.org/en/20/core/constraints.html) - Database constraints and indices
- [SQLAlchemy Migrations](https://alembic.sqlalchemy.org/en/latest/) - Database migration patterns

### Code Conventions

- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Separate core/ and storage/ layers for persistence

### Architecture Guidelines

- Database models in core/models.py
- Database connection in storage/database.py
- Migration scripts for schema changes
- Comprehensive relationship mappings
- Proper cascade behaviors for data integrity

## Success Criteria

1. All four new models (Permission, Role, RolePermission, OrganizationMembership) compile successfully
2. All unique constraints work correctly (case-insensitive name validation)
3. All foreign key constraints are properly enforced
4. Role-permission resolution works through association table
5. Organization membership creation supports both with and without roles
6. Database migration runs cleanly
7. User and Organization models extended with relationship properties
8. 90% test coverage achieved for new models
9. All edge cases handled gracefully
10. Code follows project conventions and standards

## Non-Goals / Future Work

- Soft deletes or archival support (not specified in requirements)
- Multi-organization ownership per user (explicitly noted as future)
- Organization invitations/invitability rules (future phase)
- Permission inheritance through role hierarchy (future enhancement)
- Audit logging for role/permission changes (future phase)

## Examples Required

### Sample Role with 2 Permissions
```python
# Example test data creation
def create_sample_role_with_permissions():
    """Create sample role with associated permissions for testing."""
    org = Organization(name="Sample Bowling Center", address="123 Strike Lane")
    
    # Create permissions
    perm1 = Permission(name="manage_tournaments", description="Can create and manage tournaments", organization=org)
    perm2 = Permission(name="view_reports", description="Can view tournament reports", organization=org)
    
    # Create role
    role = Role(name="Tournament Manager", organization=org)
    
    # Associate permissions with role
    role_perm1 = RolePermission(role=role, permission=perm1)
    role_perm2 = RolePermission(role=role, permission=perm2)
    
    return org, role, [perm1, perm2], [role_perm1, role_perm2]
```

### Sample Membership with Role
```python
# Example membership creation
def create_sample_membership_with_role():
    """Create sample user membership with role assignment."""
    user = User(first_name="John", last_name="Doe", email="john@example.com")
    org, role, permissions, role_perms = create_sample_role_with_permissions()
    
    # Create membership with role
    membership = OrganizationMembership(
        user=user,
        organization=org,
        role=role,
        is_registered=True  # User has email
    )
    
    return membership
```

## Edge Cases

### Data Validation Edge Cases

- **Duplicate names differing only by case**: Permission/Role names "Manager" and "manager" should be rejected as duplicates within same organization
- **Membership creation with invalid role ID**: Should fail with foreign key constraint error
- **Role assigned to non-existent permission**: RolePermission creation should fail FK constraint
- **Permissions reused across roles**: Multiple roles can have same permission (allowed many-to-many)
- **Cross-organization name conflicts**: Same permission/role names allowed across different organizations
- **Orphaned associations**: RolePermission entries should cascade delete when parent role or permission is deleted

### Relationship Edge Cases

- **User with multiple organization memberships**: Supported through separate membership records
- **Role without permissions**: Allowed (role may have permissions added later)
- **Permission without roles**: Allowed (permission may be assigned to roles later)
- **Membership without role**: Allowed (basic membership without specific role assignment)
- **Role hierarchy cycles**: Future parent_role_id implementation should prevent circular references

## Order Dependencies

- Must be implemented before any other organization feature that uses roles, permissions, or membership
- Requires existing User and Organization models to be in place
- Database migration must be applied before any role/permission-dependent features
- Should be completed before implementing organization management commands that rely on these relationships

## Migration Requirements

### Migration Script Structure
```python
"""Add organization data models

Revision ID: org_data_models_001
Revises: previous_migration_id
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Create organization data model tables."""
    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'organization_id', name='uq_permission_name_org')
    )
    
    # Create additional tables following same pattern...
    # Create indices for performance optimization...

def downgrade():
    """Drop organization data model tables."""
    op.drop_table('organization_memberships')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
```