# Product Requirements Prompt: Create Users Management (Phase 1-C)

## Summary

Implement a flexible user creation system for the 4th Arrow Tournament Control application. This feature provides CLI command to create both full members (with optional email) and temporary/non-member participants (name only) with validation and persistence in SQLite database, supporting later promotion and access to scores, tournaments, and history.

## Step-by-Step Plan

### Phase 1: CLI Command Implementation

1. Create `create` command with required and optional arguments
2. Implement validation for required fields (first, last names)
3. Add duplicate email detection with appropriate error handling
4. Set default `is_member = False` for user classification

### Phase 2: Database Integration

1. Integrate with existing SQLAlchemy User model
2. Implement data persistence in `inventory.db`
3. Handle database connection and transaction management
4. Support both member and non-member user types

### Phase 3: Validation and Testing

1. Write comprehensive test suite covering all scenarios
2. Ensure 85% test coverage as per project standards
3. Validate edge cases and error conditions
4. Test member vs non-member creation paths

## File List

### Core Implementation Files

- `src/commands/create.py` - Create user command implementation
- `core/models.py` - Existing SQLAlchemy User model (reference)
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with create command

### Test Files

- `tests/test_create_user.py` - Create user command unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click) - existing

## CLI Interface

### Command Syntax

```bash
# Create non-member user (bowler)
./run create --first Bob --last Lane

# Create full member with email
./run create --first Alice --last Smith --email alice@example.com

# Create user with all optional fields
./run create --first John --last Doe --email john@example.com --phone 555-1234 --address "123 Main St" --usbc_id 12345 --tnba_id 67890
```

### Arguments

**Required:**

- `--first` - First name (string, non-empty)
- `--last` - Last name (string, non-empty)

**Optional:**

- `--address` - User address (string)
- `--usbc_id` - USBC ID (string)
- `--tnba_id` - TNBA ID (string)
- `--phone` - Phone number (string)
- `--email` - Email address (string, triggers member status consideration)

### Error Handling

- Duplicate email (only if `--email` provided): Exit code 2, suggest `get-profile` command
- Empty first or last name: Exit code 3, descriptive error message
- Database errors: Exit code 1, user-friendly error message

## Validations

### pytest Test Coverage

- **create** command tests:
  - ✅ Create user with required args only (first, last) - non-member
  - ✅ Create user with all optional args - member
  - ✅ Create user with no email (non-member)
  - 🚫 Duplicate email returns error code 2 (only when email provided)
  - 🚫 Empty --first returns error code 3
  - 🚫 Empty --last returns error code 3
  - ✅ Successful user creation persists to database
  - ✅ User creation with partial optional fields
  - ✅ Non-member users created successfully without email
  - ✅ Default `is_member = False` set correctly

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- Both member and non-member creation paths tested

## Technical Specifications

### Database Schema

Uses existing User model from `core/models.py` with additional consideration for:

```python
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=True)  # Optional for non-members
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    usbc_id = Column(String, nullable=True)
    tnba_id = Column(String, nullable=True)
    is_member = Column(Boolean, default=False, nullable=False)  # New field consideration
    # ... other existing fields
```

### Implementation Requirements

- Code location: `src/commands/create.py`
- Follow PEP 8 compliance
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Set default `is_member = False` for all new users
- Handle email uniqueness only when email is provided

## References to Examples/Docs

### External Documentation

- [SQLAlchemy Quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) - Database ORM usage
- [Click Documentation](https://click.palletsprojects.com/) - CLI argument parsing
- CLAUDE.md - Project code style, test coverage, and structure

### Code Conventions

- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Separate core/ and storage/ layers for persistence

### Architecture Guidelines

- CLI entry points in main.py
- Command implementation in src/commands/create.py
- Database models in core/models.py
- Database connection in storage/database.py
- Comprehensive test coverage with pytest

## Success Criteria

1. Users can successfully create both member and non-member users
2. Non-member users (no email) are created successfully with `is_member = False`
3. Optional fields are properly handled and stored
4. Duplicate email detection works with exit code 2 (only when email provided)
5. Empty first/last name validation works with exit code 3
6. All data is properly persisted in `inventory.db`
7. Test coverage ≥ 85% achieved
8. All edge cases handled gracefully
9. Code follows project conventions and standards
10. Integration with existing user management system maintained
11. Users without email can be created successfully

## Non-Goals / Future

- User promotion to member (handled in future phase)
- Profile editing capabilities (covered in Phase 1-B)
- User authentication/login (covered in Phase 1-A)
- GUI flows (deferred to Phase N)
- Password storage (bcrypt) - Phase 2
- User deletion (separate feature)

## Example Usage

```bash
# Create non-member bowler
./run create --first Bob --last Lane

# Create full member with email
./run create --first Alice --last Smith --email alice@example.com

# Full user creation with all details
./run create --first John --last Doe --email john@example.com --phone 555-1234 --address "123 Main St" --usbc_id 12345 --tnba_id 67890
```

## Edge Cases

- Empty string for `--first` or `--last` → Exit code 3
- Duplicate email (only if `--email` is supplied) → Exit code 2, suggest `get-profile`
- If `--usbc_id` or `--tnba_id` already exists in the database → Exit code 2
- In future slices:
  - If no ID or email match, but `first`, `last`, and one of `phone` or `address` matches → prompt user to resolve potential duplicates (e.g. "Did you mean this existing profile?")
- Users without email should be created successfully
- Database connection failures
- Invalid data type handling
- SQL injection prevention (via SQLAlchemy ORM)
- Non-member users can participate in tournaments without email
- Future promotion of non-members to members by adding email later
