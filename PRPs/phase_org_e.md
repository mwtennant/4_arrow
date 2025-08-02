# Product Requirements Prompt: Remove User from Organization (Phase Org-E)

## Summary

Implement an organization membership removal system for the 4th Arrow Tournament Control application. This feature provides a CLI command to remove one or more existing users from organizations by their user ID, enabling flexible tournament participation management with proper validation, graceful error handling for non-members, and batch processing capabilities with partial success support.

## Step-by-Step Plan

### Slice 1: CLI Command Implementation

1. Create `remove-org-user` command with required `--organization-id` argument
2. Implement multiple `--user-id` flag support for batch operations
3. Add optional `--force` flag for future-compatible destructive batch actions
4. Implement user ID deduplication for duplicate entries
5. Validate command arguments and provide clear error messages

### Slice 2: Database Integration and Validation

1. Integrate with existing OrganizationMembership model in `core/models.py`
2. Validate organization existence using Organization model
3. Query and validate user membership in specified organization
4. Implement membership removal using SQLAlchemy ORM
5. Handle database transaction management for batch operations

### Slice 3: Error Handling and Edge Cases

1. Implement comprehensive error handling with specific exit codes
2. Handle graceful skipping of non-member users with warnings
3. Support partial success scenarios (some users removed, others skipped)
4. Provide clear success and error messages for each operation
5. Ensure clean execution even with mixed valid/invalid scenarios

### Slice 4: Testing and Validation

1. Write comprehensive test suite covering all success and error scenarios
2. Test batch operations with mixed valid/invalid users
3. Ensure 85% test coverage as per project standards
4. Validate edge cases including empty organizations and duplicate user IDs
5. Test all exit codes and error message scenarios

## File List

### Core Implementation Files

- `src/commands/remove_org_user.py` - Remove organization user command implementation
- `core/models.py` - Existing models (Organization, User, OrganizationMembership) - reference
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with remove-org-user command

### Test Files

- `tests/test_remove_org_user.py` - Remove organization user command unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click) - existing

## CLI Interface

### Command Syntax

```bash
# Remove single user from organization
./run remove-org-user --organization-id 1 --user-id 123

# Remove multiple users from organization
./run remove-org-user --organization-id 1 --user-id 123 --user-id 456 --user-id 789

# Remove multiple users with comma-separated list (future enhancement)
./run remove-org-user --organization-id 1 --user-id 123,456,789

# Remove with force flag for batch confirmation (future-compatible)
./run remove-org-user --organization-id 1 --user-id 123 --user-id 456 --force
```

### Arguments

**Required:**

- `--organization-id` - Organization ID (integer, must exist in database)
- `--user-id` - User ID(s) (integer, can be passed multiple times, must be valid user IDs)

**Optional:**

- `--force` - Force flag for destructive batch actions (future-compatible, currently no-op)

### Success Output

```bash
# Single user removal success
User 123 successfully removed from organization 1

# Multiple users success
Successfully removed the following users from organization 1:
- User 123
- User 456
- User 789

# Partial success example
Successfully removed the following users from organization 1:
- User 123
- User 456

Skipped the following users:
- User 789: Not a member of organization 1
- User 999: User not found
```

### Error Handling

- Missing required arguments: Exit code 1, message "Missing required arguments: organization-id and user-id are required"
- Organization not found: Exit code 2, message "Organization with ID {id} not found"
- No user IDs provided: Exit code 5, message "No user IDs provided"
- All users invalid/non-members: Partial success with warnings, Exit code 0

## Validations

### pytest Test Coverage

- **remove-org-user** command tests:
  - ✅ Remove one valid user from organization
  - ✅ Remove multiple valid users from organization
  - ✅ Partial success: some users valid members, some not in org (skip with warning)
  - ✅ Partial success: some users valid, some non-existent (skip with warning)
  - ✅ Duplicate user IDs in same command are deduplicated
  - ✅ Organization with no users handles cleanly
  - ✅ Success when at least one operation completes or is skipped
  - 🚫 Organization not found returns exit code 2
  - 🚫 No users provided returns exit code 5
  - 🚫 Missing organization ID returns exit code 1
  - ✅ User not in organization skipped with warning (no hard error)
  - ✅ Non-existent user skipped with warning (no hard error)
  - ✅ Database transaction safety for batch operations
  - ✅ OrganizationMembership records removed correctly

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- Partial success scenarios tested
- Batch operation scenarios tested

## Technical Specifications

### Database Schema

Uses existing models from `core/models.py`:

```python
class OrganizationMembership(Base):
    __tablename__ = 'organization_memberships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Constraints ensure unique user-organization pairs
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
    )
```

### Implementation Requirements

- Code location: `src/commands/remove_org_user.py`
- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Handle batch processing for multiple users with transaction safety
- Implement graceful skipping for non-member users with clear warnings
- Support duplicate user ID deduplication within single command

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
- Command implementation in src/commands/remove_org_user.py
- Database models in core/models.py
- Database connection in storage/database.py
- Comprehensive test coverage with pytest

### Existing Model References

- Organization model with membership relationships
- User model supporting both registered/unregistered users
- OrganizationMembership model with unique constraints
- Database transaction patterns from existing commands

## Success Criteria

1. Users can be successfully removed from organizations individually or in batches
2. Non-member users are gracefully skipped with warnings (no hard errors)
3. Non-existent users are gracefully skipped with warnings
4. Partial success scenarios handle mixed valid/invalid users gracefully
5. Organization validation provides specific error messages
6. Database operations are atomic and handle transaction rollback properly
7. Test coverage ≥ 85% achieved with comprehensive edge case coverage
8. Code follows project conventions and standards
9. Multiple user IDs can be processed in a single command execution
10. Duplicate user IDs within command are silently deduplicated
11. Command exits successfully if at least one operation completes or is skipped

## Non-Goals / Future Work

- Support removing users by email or name (vs ID) - future enhancement
- Bulk removal confirmation prompts - handled by optional --force flag
- User role modification during removal - separate edit-org-user command
- Organization member listing - separate list-org-users command
- Cascading removal from all organizations - separate command
- Remove all members from organization - separate command

## Example Usage

```bash
# Remove single user from organization
./run remove-org-user --organization-id 1 --user-id 123

# Remove multiple users from organization
./run remove-org-user --organization-id 1 --user-id 123 --user-id 456 --user-id 789

# Batch removal with force flag (future-compatible)
./run remove-org-user --organization-id 2 --user-id 100 --user-id 200 --force
```

## Edge Cases

### Data Validation

- Organization ID must exist in database → Exit code 2 if not found
- User IDs can be non-existent → Skip with warning, continue processing
- User not member of organization → Skip with warning, continue processing
- Empty organization (no members) → Command should validate and exit cleanly

### Command Processing

- Duplicate `--user-id` values in same command → Deduplicate silently
- No users provided → Exit code 5 with clear message
- Missing organization ID → Exit code 1 with clear message
- All users are non-members or non-existent → Success with warnings

### Database Operations

- Database connection failures → Exit code 1 with user-friendly message
- Transaction rollback on critical errors → Maintain data consistency
- Concurrent membership removal attempts → Handle gracefully
- Organization with complex role hierarchies → Remove membership regardless of role

### Partial Success Scenarios

- Some users are members, some are not → Remove members, warn about non-members
- Some users exist, some don't → Process existing users, warn about non-existent
- Mix of error conditions → Process all valid operations, report all issues
- Success criteria: Exit successfully if at least one operation completes or is skipped