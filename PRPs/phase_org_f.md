# Product Requirements Prompt: Create Organization Permissions (Phase Org-F)

## Summary

Implement organization-level permission management for the 4th Arrow Tournament Control application. This feature provides CLI command to create organization-scoped permissions that can later be assigned to roles, establishing the foundation for role-based access control within organizations. Permissions are unique within each organization (case-insensitive) and support optional descriptions for clarity.

## Step-by-Step Plan

### Slice 1: CLI Command Implementation

1. Create `create-org-permission` command with required and optional arguments
2. Implement validation for required fields (organization_id, name)
3. Add duplicate permission name detection (case-insensitive) within organization scope
4. Create and persist new Permission records with unique permission IDs

### Slice 2: Database Integration and Validation

1. Utilize existing SQLAlchemy Permission model from `core/models.py`
2. Implement data persistence in `tournament_control.db`
3. Handle database connection and transaction management via existing `storage/database.py`
4. Support permission name uniqueness with case-insensitive validation within organization scope
5. Validate organization exists before creating permission

### Slice 3: Validation and Testing

1. Write comprehensive test suite covering all scenarios
2. Ensure 85% test coverage as per project standards
3. Validate edge cases and error conditions
4. Test permission creation and uniqueness validation within organization scope

## File List

### Core Implementation Files

- `src/commands/create_org_permission.py` - Create organization permission command implementation
- `core/models.py` - Existing SQLAlchemy Permission model (reference)
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with create-org-permission command

### Test Files

- `tests/test_create_org_permission.py` - Create organization permission command unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click) - existing

## CLI Interface

### Command Syntax

```bash
# Create permission with name only
./run create-org-permission --organization-id 1 --name "Create Tournament"

# Create permission with name and description
./run create-org-permission --organization-id 1 --name "Manage Users" --description "Full access to user management within organization"

# Create permission with long description
./run create-org-permission --organization-id 2 --name "View Reports" --description "Read-only access to tournament reports, scores, and analytics data for organizational oversight"
```

### Arguments

**Required:**

- `--organization-id` - Organization ID (integer, must reference existing organization)
- `--name` - Permission name (string, non-empty, unique within organization case-insensitive, ≤ 64 chars)

**Optional:**

- `--description` - Permission description (string, ≤ 255 chars, can be empty)

### Success Output

```bash
Permission created successfully!
Permission ID: 1
Name: Create Tournament
Description: Full access to tournament creation and management
Organization ID: 1
```

### Error Handling

- Missing required field (`--organization-id` or `--name`): Exit code 1, message "Missing required field: {field_name}"
- Organization not found: Exit code 2, message "Organization with ID {id} not found"
- Duplicate permission name (case-insensitive within org): Exit code 3, message "Permission with this name already exists in the organization"
- Name/description length validation: Exit code 1, descriptive error message
- Database errors: Exit code 1, user-friendly error message

## Validations

### pytest Test Coverage

- **create-org-permission** command tests:
  - ✅ Create permission with required args only (organization_id, name)
  - ✅ Create permission with name and description
  - ✅ Successful permission creation persists to database with generated ID
  - 🚫 Duplicate permission name within organization returns error code 3 (case-insensitive)
  - 🚫 Missing --organization-id returns error code 1
  - 🚫 Missing --name returns error code 1
  - 🚫 Organization not found returns error code 2
  - 🚫 Permission name exceeds 64 characters returns error code 1
  - 🚫 Description exceeds 255 characters returns error code 1
  - ✅ Permission name case sensitivity (different cases treated as duplicate within org)
  - ✅ Same permission name in different organizations allowed
  - ✅ Permission name with extra whitespace handled correctly
  - ✅ Multi-word permission names supported
  - ✅ Empty description allowed
  - ✅ Special characters in permission name validation

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- Permission uniqueness validation tested within organization scope

## Technical Specifications

### Database Schema

Uses existing Permission model from `core/models.py`:

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

### Implementation Requirements

- Code location: `src/commands/create_org_permission.py`
- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Implement case-insensitive name uniqueness validation within organization scope
- Handle whitespace normalization for permission names
- Validate organization existence before creating permission

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
- Follow existing command structure and error handling patterns
- Use existing database session management patterns from `storage/database.py`

## Success Criteria

1. Permissions can be successfully created with valid organization_id and name
2. Duplicate permission names within same organization are properly rejected (case-insensitive)
3. Same permission names in different organizations are allowed
4. Organization existence is validated before creating permission
5. Permission data is securely stored in SQLite with generated IDs
6. All data validation works correctly (name ≤ 64 chars, description ≤ 255 chars)
7. 85% test coverage achieved
8. All edge cases handled gracefully
9. Code follows project conventions and standards
10. Empty descriptions are properly handled
11. Special characters in names are validated appropriately

## Non-Goals / Future Work

- Assigning permissions to roles (see phase-org-g)
- Editing or deleting permissions (future phase)
- Permission templates or defaults per organization type (future phase)
- Permission hierarchies or inheritance (future phase)
- Bulk permission creation (future phase)

## Example Usage

```bash
# Create basic permission
./run create-org-permission --organization-id 1 --name "Create Tournament"

# Create permission with description
./run create-org-permission --organization-id 1 --name "Manage Users" --description "Full access to user management within organization"

# This should fail - duplicate name in same org
./run create-org-permission --organization-id 1 --name "create tournament"
# Error: Permission with this name already exists in the organization

# This should succeed - same name in different org
./run create-org-permission --organization-id 2 --name "Create Tournament"
```

## Edge Cases

- Permission name with extra spaces or mixed case → normalized and treated as potential duplicate within organization
- Empty string for description → allowed and stored as NULL/empty
- Organization ID that doesn't exist → Exit code 2 with clear error message
- Permission name with special characters → validate as needed (alphanum + spaces + common punctuation)
- Long names or descriptions → validated against length limits (64 chars for name, 255 for description)
- Database connection failures → graceful error handling with user-friendly messages
- Concurrent creation attempts with same name in same org → proper uniqueness constraint handling
- Mixed case duplicate checking ("Create Tournament" vs "create tournament" in same org) → reject as duplicate
- Same permission name in different organizations → should be allowed
- Permission name with only whitespace → proper validation errors after trimming
- Special database characters that might cause issues → proper escaping via SQLAlchemy ORM

## Test Cases

### Positive Test Cases

- ✅ Create permission with name only
- ✅ Create permission with name + description
- ✅ Create permission with empty description
- ✅ Create same permission name in different organizations
- ✅ Create permission with maximum length name (64 chars)
- ✅ Create permission with maximum length description (255 chars)

### Negative Test Cases

- ❌ Create duplicate permission in same org → Exit 3
- ❌ Missing organization_id → Exit 1
- ❌ Missing name → Exit 1
- ❌ Organization not found → Exit 2
- ❌ Name exceeds max length → Exit 1
- ❌ Description exceeds max length → Exit 1
- ❌ Empty name (after trimming) → Exit 1