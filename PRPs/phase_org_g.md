# Product Requirements Prompt: Create Organization Roles (Phase Org-G)

## Summary

Implement organization role management for the 4th Arrow Tournament Control application. This feature provides CLI command to create roles within organizations with optional default permissions assignment, establishing the foundation for role-based access control. Roles are unique within each organization (case-insensitive) and can be assigned a set of permissions from that organization's available permissions during creation.

## Step-by-Step Plan

### Slice 1: CLI Command Implementation

1. Create `create-org-role` command with required and optional arguments
2. Implement validation for required fields (organization_id, name)
3. Add duplicate role name detection (case-insensitive) within organization scope
4. Parse and validate comma-separated permissions list
5. Create and persist new Role records with unique role IDs

### Slice 2: Database Integration and Validation

1. Utilize existing SQLAlchemy Role model from `core/models.py`
2. Implement data persistence in `tournament_control.db`
3. Handle database connection and transaction management via existing `storage/database.py`
4. Support role name uniqueness with case-insensitive validation within organization scope
5. Validate organization exists before creating role
6. Validate all specified permissions exist within the organization
7. Create RolePermission associations for each assigned permission

### Slice 3: Validation and Testing

1. Write comprehensive test suite covering all scenarios
2. Ensure 85% test coverage as per project standards
3. Validate edge cases and error conditions
4. Test role creation with and without permissions
5. Test permission validation and assignment

## File List

### Core Implementation Files

- `src/commands/create_org_role.py` - Create organization role command implementation
- `core/models.py` - Existing SQLAlchemy Role and RolePermission models (reference)
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with create-org-role command

### Test Files

- `tests/test_create_org_role.py` - Create organization role command unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click) - existing

## CLI Interface

### Command Syntax

```bash
# Create role with name only (no permissions)
./run create-org-role --organization-id 1 --name "Tournament Director"

# Create role with one permission
./run create-org-role --organization-id 1 --name "User Manager" --permissions "Manage Users"

# Create role with multiple permissions (comma-separated)
./run create-org-role --organization-id 1 --name "Admin" --permissions "Create Tournament,Manage Users,View Reports"

# Create role with permissions containing spaces
./run create-org-role --organization-id 2 --name "Event Coordinator" --permissions "Create Tournament, Edit Scores, Generate Reports"
```

### Arguments

**Required:**

- `--organization-id` - Organization ID (integer, must reference existing organization)
- `--name` - Role name (string, non-empty, unique within organization case-insensitive, ≤ 64 chars)

**Optional:**

- `--permissions` - Comma-separated list of permission names (string, each permission must exist in the organization)

### Success Output

```bash
Role created successfully!
Role ID: 1
Name: Tournament Director
Organization ID: 1
Permissions: Create Tournament, Manage Users, View Reports (3 permissions assigned)
```

### Error Handling

- Missing required field (`--organization-id` or `--name`): Exit code 1, message "Missing required field: {field_name}"
- Organization not found: Exit code 2, message "Organization with ID {id} not found"
- Role name already exists (case-insensitive within org): Exit code 3, message "Role with this name already exists in the organization"
- Any permission not found in organization: Exit code 4, message "Permission '{permission_name}' not found in organization"
- Role name length validation: Exit code 1, descriptive error message
- Database errors: Exit code 1, user-friendly error message

## Validations

### pytest Test Coverage

- **create-org-role** command tests:
  - ✅ Create role with name only (no permissions)
  - ✅ Create role with one valid permission
  - ✅ Create role with multiple valid permissions
  - ✅ Successful role creation persists to database with generated ID
  - ✅ Successful permission assignments create RolePermission records
  - 🚫 Duplicate role name within organization returns error code 3 (case-insensitive)
  - 🚫 Missing --organization-id returns error code 1
  - 🚫 Missing --name returns error code 1
  - 🚫 Organization not found returns error code 2
  - 🚫 Invalid permission in list returns error code 4
  - 🚫 Role name exceeds 64 characters returns error code 1
  - ✅ Role name case sensitivity (different cases treated as duplicate within org)
  - ✅ Same role name in different organizations allowed
  - ✅ Role name with extra whitespace handled correctly
  - ✅ Multi-word role names supported
  - ✅ Permissions list with whitespace trimmed correctly
  - ✅ Case-insensitive permission matching
  - ✅ Empty permissions list results in role with no permissions
  - ✅ Permissions in any order processed correctly

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- Role uniqueness validation tested within organization scope
- Permission validation and assignment tested

## Technical Specifications

### Database Schema

Uses existing Role and RolePermission models from `core/models.py`:

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

### Implementation Requirements

- Code location: `src/commands/create_org_role.py`
- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Implement case-insensitive name uniqueness validation within organization scope
- Handle whitespace normalization for role names and permission names
- Validate organization existence before creating role
- Validate all permissions exist within the organization before assignment
- Create role-permission associations in single transaction

## References to Examples/Docs

### External Documentation

- [SQLAlchemy Quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) - Database ORM usage
- [Click Documentation](https://click.palletsprojects.com/) - CLI argument parsing

### Code Conventions

- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Separate core/ and storage/ layers for persistence

### Architecture Guidelines

- CLI entry points in main.py
- Database models in core/models.py
- Database connection in storage/database.py
- Command implementation in src/commands/
- Comprehensive test coverage with pytest

### Existing Code Patterns

- Reference `src/commands/create_organization.py` for similar validation patterns
- Reference `src/commands/create_org_permission.py` for organization validation patterns
- Follow existing command structure and error handling patterns
- Use existing database session management patterns from `storage/database.py`

## Success Criteria

1. Roles can be successfully created with valid organization_id and name
2. Duplicate role names within same organization are properly rejected (case-insensitive)
3. Same role names in different organizations are allowed
4. Organization existence is validated before creating role
5. Permissions are validated to exist within the organization before assignment
6. Role data is securely stored in SQLite with generated IDs
7. RolePermission associations are created correctly for assigned permissions
8. All data validation works correctly (name ≤ 64 chars)
9. 85% test coverage achieved
10. All edge cases handled gracefully
11. Code follows project conventions and standards
12. Comma-separated permissions are parsed and validated correctly
13. Case-insensitive permission matching works properly
14. Roles without permissions are created successfully

## Non-Goals / Future Work

- Editing or deleting roles (future phase)
- Role hierarchies or inheritance (parent_role_id field exists for future use)
- Assigning users to roles (see organization membership features)
- Role templates or defaults per organization type (future phase)
- Bulk role creation (future phase)
- Role permission modification after creation (future phase)

## Example Usage

```bash
# Create basic role with no permissions
./run create-org-role --organization-id 1 --name "Basic User"

# Create role with single permission
./run create-org-role --organization-id 1 --name "Tournament Creator" --permissions "Create Tournament"

# Create role with multiple permissions
./run create-org-role --organization-id 1 --name "Admin" --permissions "Create Tournament,Manage Users,View Reports"

# This should fail - duplicate name in same org
./run create-org-role --organization-id 1 --name "basic user"
# Error: Role with this name already exists in the organization

# This should succeed - same name in different org
./run create-org-role --organization-id 2 --name "Basic User"

# This should fail - invalid permission
./run create-org-role --organization-id 1 --name "Invalid Role" --permissions "Nonexistent Permission"
# Error: Permission 'Nonexistent Permission' not found in organization
```

## Edge Cases

- Role name with extra spaces or mixed case → normalized and treated as potential duplicate within organization
- Organization ID that doesn't exist → Exit code 2 with clear error message
- Permission names with extra spaces in comma-separated list → trimmed and validated
- Permission names with mixed case → case-insensitive matching
- Long role names → validated against length limits (64 chars for name)
- Database connection failures → graceful error handling with user-friendly messages
- Concurrent creation attempts with same name in same org → proper uniqueness constraint handling
- Mixed case duplicate checking ("Admin" vs "admin" in same org) → reject as duplicate
- Same role name in different organizations → should be allowed
- Role name with only whitespace → proper validation errors after trimming
- Empty permissions list → role created with no permissions
- Permissions list with empty strings or just commas → properly filtered and validated
- Permission that exists but in different organization → proper error handling
- Special database characters in role names → proper escaping via SQLAlchemy ORM
- Transaction rollback if any permission assignment fails → ensure data consistency

## Test Cases

### Positive Test Cases

- ✅ Create role with name only (no permissions)
- ✅ Create role with one permission
- ✅ Create role with multiple permissions
- ✅ Create same role name in different organizations
- ✅ Create role with maximum length name (64 chars)
- ✅ Create role with permissions in any order
- ✅ Create role with case-insensitive permission matching

### Negative Test Cases

- ❌ Create duplicate role in same org → Exit 3
- ❌ Missing organization_id → Exit 1
- ❌ Missing name → Exit 1
- ❌ Organization not found → Exit 2
- ❌ Name exceeds max length → Exit 1
- ❌ Invalid permission in list → Exit 4
- ❌ Empty name (after trimming) → Exit 1
- ❌ Permission from different organization → Exit 4