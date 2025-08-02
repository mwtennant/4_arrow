# Product Requirements Prompt: User Signup and Authentication

## Summary

Implement a user management system for the 4th Arrow Tournament Control application. This feature provides basic user signup and authentication functionality with SQLite persistence, serving as the foundation for member management in the tournament system.

## Step-by-Step Plan

### Phase User: Database Schema and Models

1. Create SQLAlchemy models for User entity
2. Set up database connection and table creation
3. Configure bcrypt for password hashing

### Phase 2: CLI Commands Implementation

1. Implement `signup` command with required and optional arguments
2. Implement `login` command with email/password validation
3. Add proper error handling and user feedback

### Phase 3: Validation and Testing

1. Write comprehensive test suite covering all scenarios
2. Ensure 85% test coverage as per project standards
3. Validate edge cases and error conditions

## File List

### Core Implementation Files

- `main.py` - CLI entry point with signup/login commands
- `core/auth.py` - Authentication logic and password hashing
- `core/models.py` - SQLAlchemy User model
- `storage/database.py` - Database connection and initialization

### Test Files

- `tests/test_auth.py` - Authentication unit tests
- `tests/test_models.py` - Model validation tests
- `tests/test_cli.py` - CLI command integration tests

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, bcrypt, click)

## Validations

### pytest Test Coverage

- **signup** command tests:
  - Valid user creation with all required fields
  - Optional fields handling (address, usbc_id, tnba_id)
  - Duplicate email rejection with exit code 1
  - Empty email/password validation
  - Invalid email format validation
- **login** command tests:
  - Successful authentication with valid credentials
  - Authentication failure with wrong credentials (exit code 1)
  - Empty credential handling
- **Model tests**:
  - User creation and validation
  - Password hashing verification
  - Database persistence

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested

## Technical Specifications

### Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT,
    usbc_id TEXT,
    tnba_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### CLI Interface

```bash
# Signup command
python main.py signup --email user@example.com --password secret123 --first John --last Doe --phone 555-1234 [--address "123 Main St"] [--usbc_id 12345] [--tnba_id 67890]

# Login command
python main.py login --email user@example.com --password secret123
```

### Error Handling

- Duplicate email: Exit code 1, message "Email already exists"
- Invalid credentials: Exit code 1, message "Invalid email or password"
- Missing required fields: Exit code 1, descriptive error message
- Database errors: Exit code 1, user-friendly error message

## References to Examples/Docs

### External Documentation

- [bcrypt Python library](https://pypi.org/project/bcrypt/) - For secure password hashing
- [SQLAlchemy Quickstart](https://docs.sqlalchemy.org/en/20/tutorial/) - Database ORM usage
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework

### Code Conventions

- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Separate core/ and storage/ layers for persistence

### Architecture Guidelines

- CLI entry points in main.py
- Authentication logic in core/auth.py
- Database models in core/models.py
- Database connection in storage/database.py
- Comprehensive test coverage with pytest

## Success Criteria

1. Users can successfully create accounts with valid credentials
2. Duplicate email registration is properly rejected
3. Users can authenticate with correct credentials
4. Invalid login attempts are properly handled
5. All data is securely stored in SQLite with hashed passwords
6. 100% test coverage achieved
7. All edge cases handled gracefully
8. Code follows project conventions and standards
