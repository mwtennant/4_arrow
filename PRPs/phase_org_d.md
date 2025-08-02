# Product Requirements Prompt: Add User to Organization (Phase Org-D)

## Summary

Implement an organization membership management system for the 4th Arrow Tournament Control application. This feature provides CLI command to assign existing users (both registered and unregistered) to organizations with optional role assignment, enabling flexible tournament participation management across multiple organizations with proper validation and conflict detection.

## Step-by-Step Plan

### Slice 1: CLI Command Implementation

1. Create `add-org-user` command with required and optional arguments
2. Implement validation for organization existence and user existence
3. Add duplicate membership detection with appropriate error handling
4. Support multiple user assignment in a single command execution
5. Implement role validation and assignment when provided

### Slice 2: Database Integration and Validation

1. Integrate with existing OrganizationMembership model in `core/models.py`
2. Validate organization existence using Organization model
3. Validate user existence using User model (both registered/unregistered)
4. Validate role existence within the specified organization
5. Handle database transaction management for batch operations

### Slice 3: Error Handling and Edge Cases

1. Implement comprehensive error handling with specific exit codes
2. Handle partial success scenarios (some users added, others skipped)
3. Support role case-insensitive matching
4. Implement duplicate user ID deduplication in single command
5. Provide clear error messages for each failure scenario

### Slice 4: Testing and Validation

1. Write comprehensive test suite covering all scenarios
2. Ensure 85% test coverage as per project standards
3. Test both registered and unregistered user assignment
4. Validate edge cases and error conditions
5. Test batch operations and partial success scenarios

## File List

### Core Implementation Files

- `src/commands/add_org_user.py` - Add organization user command implementation
- `core/models.py` - Existing models (Organization, User, OrganizationMembership, Role) - reference
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with add-org-user command

### Test Files

- `tests/test_add_org_user.py` - Add organization user command unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click) - existing

## CLI Interface

### Command Syntax

```bash
# Add one user with role to organization
./run add-org-user --organization-id 1 --user-id 123 --role Manager

# Add multiple users without role
./run add-org-user --organization-id 1 --user-id 123 --user-id 456 --user-id 789

# Add multiple users with specific role
./run add-org-user --organization-id 2 --user-id 100 --user-id 200 --role "Tournament Director"
```

### Arguments

**Required:**

- `--organization-id` - Organization ID (integer, must exist in database)
- `--user-id` - User ID(s) (integer, can be passed multiple times, must exist in database)

**Optional:**

- `--role` - Role name (string, must exist within the specified organization, case-insensitive)

### Success Output

```bash
# Single user success
User 123 successfully added to organization 1 with role 'Manager'

# Multiple users success
Successfully added the following users to organization 1:
- User 123 (role: Manager)
- User 456 (role: Manager) 
- User 789 (role: Manager)

# Partial success example
Successfully added the following users to organization 1:
- User 123 (role: Manager)
- User 456 (role: Manager)

Skipped the following users:
- User 789: Already a member of organization 1
- User 999: User not found
```

### Error Handling

- Missing required arguments: Exit code 1, message "Missing required arguments"
- Organization not found: Exit code 2, message "Organization with ID {id} not found"
- User already member: Exit code 3, message "User {user_id} is already a member of organization {org_id}"
- Role not found: Exit code 4, message "Role '{role}' not found in organization {org_id}"
- No users provided: Exit code 5, message "No users provided"

## Validations

### pytest Test Coverage

- **add-org-user** command tests:
  - ✅ Add one valid user with valid role
  - ✅ Add one valid user without role (null role_id)
  - ✅ Add multiple valid users with role
  - ✅ Add multiple valid users without role
  - ✅ Partial success: some users valid, some already members
  - ✅ Partial success: some users valid, some non-existent
  - ✅ Role case-insensitive matching ("Manager" == "manager")
  - ✅ Duplicate user IDs in same command are deduplicated
  - ✅ Both registered and unregistered users can be added
  - 🚫 Organization not found returns exit code 2
  - 🚫 All users already members returns exit code 3
  - 🚫 Role not found returns exit code 4
  - 🚫 No users provided returns exit code 5
  - 🚫 Missing organization ID returns exit code 1
  - 🚫 Invalid user ID (non-existent) handled gracefully
  - ✅ Database transaction rollback on critical errors
  - ✅ OrganizationMembership records created correctly

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- Both registered and unregistered user scenarios tested
- Partial success scenarios tested

## Technical Specifications

### Database Schema

Uses existing models from `core/models.py`:

```python
class OrganizationMembership(Base):
    __tablename__ = 'organization_memberships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)  # Optional role
    created_at = Column(DateTime, default=func.now())
    
    # Constraints ensure unique user-organization pairs
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
    )
```

### Implementation Requirements

- Code location: `src/commands/add_org_user.py`
- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Handle both registered users (with email) and unregistered users (name only)
- Support case-insensitive role matching with proper normalization
- Implement batch processing for multiple users with transaction safety

## References to Examples/Docs

### External Documentation

- [SQLAlchemy Quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) - Database ORM usage
- [Click Documentation](https://click.palletsprojects.com/) - CLI argument parsing with multiple values

### Code Conventions

- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Separate core/ and storage/ layers for persistence

### Architecture Guidelines

- CLI entry points in main.py
- Command implementation in src/commands/add_org_user.py
- Database models in core/models.py
- Database connection in storage/database.py
- Comprehensive test coverage with pytest

### Existing Model References

- Organization model with roles relationship
- User model supporting both registered/unregistered users
- OrganizationMembership model with unique constraints
- Role model with organization scoping

## Success Criteria

1. Users can be successfully added to organizations individually or in batches
2. Both registered users (with email) and unregistered users (name only) are supported
3. Role assignment works correctly with case-insensitive matching
4. Duplicate membership detection prevents conflicts with clear error messages
5. Partial success scenarios handle mixed valid/invalid users gracefully
6. Organization and role validation provides specific error messages
7. Database operations are atomic and handle transaction rollback properly
8. Test coverage ≥ 85% achieved with comprehensive edge case coverage
9. Code follows project conventions and standards
10. Multiple user IDs can be processed in a single command execution
11. Role assignment is optional with null role_id support

## Non-Goals / Future Work

- Support adding users by email or name (vs ID) - future enhancement
- Bulk imports from external sources - separate feature
- User role modification after assignment - separate edit-org-user command
- Organization member listing - separate list-org-users command
- Member removal functionality - separate remove-org-user command
- Role hierarchy or permission validation - handled by existing role system

## Example Usage

```bash
# Add single user with role
./run add-org-user --organization-id 1 --user-id 123 --role "Tournament Director"

# Add multiple users without role
./run add-org-user --organization-id 1 --user-id 123 --user-id 456 --user-id 789

# Add users with case-insensitive role matching
./run add-org-user --organization-id 2 --user-id 100 --role "manager"  # matches "Manager"
```

## Edge Cases

### Data Validation

- Organization ID must exist in database → Exit code 2 if not found
- User IDs must exist in database → Skip invalid users with warning
- Role name must exist within specified organization → Exit code 4 if not found
- User cannot already be member of organization → Exit code 3 or skip with warning

### Command Processing

- Duplicate `--user-id` values in same command → Deduplicate silently
- Empty or whitespace-only role names → Treat as no role provided
- Case variations in role names → Normalize and match case-insensitively
- No users provided → Exit code 5 with clear message

### Database Operations

- Database connection failures → Exit code 1 with user-friendly message
- Transaction rollback on critical errors → Maintain data consistency
- Concurrent membership creation attempts → Handle unique constraint violations

### User Type Support

- Registered users (with email) → Full support
- Unregistered users (name only) → Full support for tournament participation
- Users with partial profiles → Support all existing user records

### Partial Success Scenarios

- Some users valid, some already members → Add valid users, report skipped
- Some users valid, some non-existent → Add valid users, report errors
- Mix of error conditions → Process all valid operations, report all issues