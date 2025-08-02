# Product Requirements Prompt: Create Organization Management (Phase Org-A)

## Summary

Implement a flexible organization creation system for the 4th Arrow Tournament Control application. This feature provides CLI command to create new organizations with required core information and optional contact details, establishing the foundation for multi-organization tournament management with proper validation and persistence in SQLite database.

## Step-by-Step Plan

### Slice 1: CLI Command Implementation

1. Create `create-organization` command with required and optional arguments
2. Implement validation for required fields (name)
3. Add duplicate organization name detection (case-insensitive) with appropriate error handling
4. Create and persist new Organization records with unique organization IDs

### Slice 2: Database Integration

1. Create new SQLAlchemy Organization model in `core/models.py`
2. Implement data persistence in `tournament_control.db`
3. Handle database connection and transaction management via existing `storage/database.py`
4. Support organization name uniqueness with case-insensitive validation

### Slice 3: Validation and Testing

1. Write comprehensive test suite covering all scenarios
2. Ensure 85% test coverage as per project standards
3. Validate edge cases and error conditions
4. Test organization creation and uniqueness validation

## File List

### Core Implementation Files

- `src/commands/create_organization.py` - Create organization command implementation
- `core/models.py` - New SQLAlchemy Organization model
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with create-organization command

### Test Files

- `tests/test_create_organization.py` - Create organization command unit tests
- `tests/test_organization_model.py` - Organization model unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click) - existing

## CLI Interface

### Command Syntax

```bash
# Create organization with required fields
./run create-organization --name "4th Arrow Bowling Center" --address "123 Strike Lane, Bowling City, BC 12345"

# Create organization with optional contact information (future expansion)
./run create-organization --name "Pine Valley Lanes" --address "456 Pin Ave, Valley Town, VT 67890" --phone "555-BOWL" --email "info@pinevalley.com" --website "https://pinevalley.com"
```

### Arguments

**Required:**

- `--name` - Organization name (string, non-empty, must be unique case-insensitive)

**Optional (schema prepared for future support):**

- `--address` - Organization address (string, non-empty)
- `--phone` - Phone number (string)
- `--email` - Email address (string)
- `--website` - Website URL (string)

### Success Output

```bash
Organization created successfully!
Organization ID: 1
Name: 4th Arrow Bowling Center
Address: 123 Strike Lane, Bowling City, BC 12345
```

### Error Handling

- Missing required field (`--name` or `--address`): Exit code 1, message "Missing required field: {field_name}"
- Duplicate organization name (case-insensitive): Exit code 2, message "Organization with this name already exists"
- Database errors: Exit code 1, user-friendly error message

## Validations

### pytest Test Coverage

- **create-organization** command tests:
  - ✅ Create organization with required args only (name, address)
  - ✅ Create organization with all optional args (when implemented)
  - ✅ Successful organization creation persists to database with generated ID
  - 🚫 Duplicate organization name returns error code 2 (case-insensitive)
  - 🚫 Missing --name returns error code 1
  - 🚫 Missing --address returns error code 1
  - ✅ Organization name case sensitivity (different cases treated as duplicate)
  - ✅ Organization name with extra whitespace handled correctly
  - ✅ Multi-word organization names supported
  - ✅ Long names and addresses within reasonable limits

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- Organization uniqueness validation tested

## Technical Specifications

### Database Schema

New Organization model to be added to `core/models.py`:

```python
class Organization(Base):
    """Organization model for storing tournament organization information."""

    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    address = Column(Text, nullable=False)
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
```

### Implementation Requirements

- Code location: `src/commands/create_organization.py`
- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Implement case-insensitive name uniqueness validation
- Handle whitespace normalization for organization names

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

## Success Criteria

1. Organizations can be successfully created with valid name and address
2. Duplicate organization names are properly rejected (case-insensitive)
3. Organization data is securely stored in SQLite with generated IDs
4. All data validation works correctly
5. 85% test coverage achieved
6. All edge cases handled gracefully
7. Code follows project conventions and standards
8. Future-ready schema supports optional contact information

## Non-Goals / Future Work

- Organization editing capabilities (see phase-org-b)
- Role or permission setup (see phase-org-f/g)
- Linking users to organizations (see phase-org-c)
- Organization search and listing (future phase)
- Organization deletion or archival (future phase)

## Edge Cases

- Organization name with extra spaces or mixed case → normalized and treated as potential duplicate
- Long names or addresses → validated against reasonable length limits
- Multi-word names → support quoted strings in CLI
- Empty string inputs after whitespace trimming → proper validation errors
- Database connection failures → graceful error handling with user-friendly messages
- Concurrent creation attempts with same name → proper uniqueness constraint handling
