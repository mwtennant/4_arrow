# Product Requirements Prompt: List Users Management (Phase User-E)

## Summary

Implement a flexible CLI command to retrieve and filter all user profiles in the 4th Arrow Tournament Control system. This feature provides operators with a powerful search tool that supports zero or multiple filters to narrow down user results, enabling efficient user management and profile lookup operations.

## Step-by-Step Plan

### Phase User: CLI Command Implementation

1. Create `list-users` command with optional filter arguments
2. Implement individual filter validation and handling
3. Add support for combining multiple filters with logical AND operations
4. Ensure clean CLI output formatting using Rich library

### Phase 2: Database Integration

1. Integrate with existing SQLAlchemy User model from `core/models.py`
2. Implement efficient query building for dynamic filter combinations
3. Handle database connection via existing `storage/database.py`
4. Support querying from `inventory.db` database

### Phase 3: Output and Formatting

1. Implement Rich table output with proper formatting
2. Handle empty result sets gracefully
3. Ensure readable CLI output for large user lists
4. Add appropriate column headers and data presentation

### Phase 4: Validation and Testing

1. Write comprehensive test suite covering all filter scenarios
2. Ensure 85% test coverage as per project standards
3. Validate edge cases and error conditions
4. Test individual and combined filter operations

## File List

### Core Implementation Files

- `src/commands/list_users.py` - List users command implementation
- `core/models.py` - Existing SQLAlchemy User model (reference)
- `storage/database.py` - Database connection and initialization (reference)
- `main.py` - CLI entry point extension with list-users command

### Test Files

- `tests/test_list_users.py` - List users command unit tests
- `tests/test_cli.py` - CLI command integration tests (extend existing)

### Configuration Files

- `requirements.txt` - Dependencies (SQLAlchemy, click, rich) - existing

## CLI Interface

### Command Syntax

```bash
# List all users
./run list-users

# Filter by first name
./run list-users --first John

# Filter by last name
./run list-users --last Smith

# Filter by email
./run list-users --email john@example.com

# Filter by multiple fields (AND operation)
./run list-users --first John --email john@example.com

# Filter by all available fields
./run list-users --first John --last Doe --email john@example.com --phone 555-1234 --address "123 Main St" --usbc_id 12345 --tnba_id 67890
```

### Arguments

**All Optional Filter Arguments:**

- `--first` - First name filter (string, partial match)
- `--last` - Last name filter (string, partial match)
- `--address` - Address filter (string, partial match)
- `--usbc_id` - USBC ID filter (string, exact match)
- `--tnba_id` - TNBA ID filter (string, exact match)
- `--phone` - Phone number filter (string, partial match)
- `--email` - Email address filter (string, partial match)

### Output Format

- Rich table with border=MINIMAL
- Columns: user_id · first · last · email · phone · address · usbc_id · tnba_id
- Clean message when no users match filters
- Readable formatting for CLI consumption

### Error Handling

- Database connection failures: Exit code 1, user-friendly error message
- No matching users: Exit code 0, clean "No users found" message
- Invalid filter values: Handled gracefully with appropriate messaging

## Validations

### pytest Test Coverage

- **list-users** command tests:
  - ✅ Returns all users when no filters are applied
  - ✅ Returns correct subset with `--first` filter
  - ✅ Returns correct subset with `--last` filter
  - ✅ Returns correct subset with `--email` filter
  - ✅ Returns correct subset with `--phone` filter
  - ✅ Returns correct subset with `--address` filter
  - ✅ Returns correct subset with `--usbc_id` filter
  - ✅ Returns correct subset with `--tnba_id` filter
  - ✅ Returns correct subset when multiple filters are applied (AND logic)
  - ✅ Returns correct subset when all filters are applied
  - ✅ Returns empty result when no users match the filter (Edge Case)
  - ✅ Handles database connection failures gracefully
  - ✅ Displays clean output formatting with Rich tables
  - ✅ Properly handles partial string matching for applicable fields
  - ✅ Properly handles exact matching for ID fields

### Coverage Requirements

- Minimum 85% coverage as per CLAUDE.md standards
- All edge cases covered in tests
- Error handling paths tested
- All filter combinations tested
- Output formatting tested

## Technical Specifications

### Database Query Implementation

Uses existing User model from `core/models.py` with dynamic filter building:

```python
def build_user_query(session, filters: Dict[str, str]) -> Query:
    """Build SQLAlchemy query with dynamic filters."""
    query = session.query(User)

    if filters.get('first'):
        query = query.filter(User.first_name.ilike(f"%{filters['first']}%"))
    if filters.get('last'):
        query = query.filter(User.last_name.ilike(f"%{filters['last']}%"))
    if filters.get('email'):
        query = query.filter(User.email.ilike(f"%{filters['email']}%"))
    # ... other filters with appropriate matching logic

    return query
```

### Implementation Requirements

- Code location: `src/commands/list_users.py`
- Follow PEP 8 compliance
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Integrate with existing database layer in `storage/database.py`
- Use Rich library for table output formatting
- Implement logical AND operations for multiple filters

### Filter Logic

- String fields (`first`, `last`, `email`, `phone`, `address`): Case-insensitive partial matching
- ID fields (`usbc_id`, `tnba_id`): Exact matching
- Multiple filters: Combined with logical AND (not OR)
- Empty filters ignored in query building

## References to Examples/Docs

### External Documentation

- [SQLAlchemy Quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) - Database ORM usage
- [Click Documentation](https://click.palletsprojects.com/) - CLI argument parsing
- [Rich Documentation](https://rich.readthedocs.io/) - Terminal formatting and tables
- CLAUDE.md - Project code style, test coverage, and structure

### Code Conventions

- Follow PEP 8 compliance as specified in CLAUDE.md
- Use type hints for all function signatures
- Implement Google-style docstrings
- Use snake_case for variables/functions, PascalCase for classes
- Separate core/ and storage/ layers for persistence

### Architecture Guidelines

- CLI entry points in main.py
- Command implementation in src/commands/list_users.py
- Database models in core/models.py
- Database connection in storage/database.py
- Comprehensive test coverage with pytest

## Success Criteria

1. Users can successfully list all users without filters
2. Each individual filter works correctly with appropriate matching logic
3. Multiple filters combine with logical AND operations
4. Empty result sets are handled gracefully with clean messaging
5. Rich table output is properly formatted and readable
6. All data is properly queried from `inventory.db`
7. Test coverage ≥ 85% achieved
8. All edge cases handled gracefully
9. Code follows project conventions and standards
10. Integration with existing user management system maintained
11. Performance is acceptable for reasonable user database sizes

## Non-Goals / Future Work

- Filtering by:
  - Tournament participation data
  - Organization membership status
  - Scoring data (high/low games, averages, etc.)
  - Creation/modification timestamps
- Pagination for large result sets
- Sorting options (alphabetical, by ID, etc.)
- Export to CSV/JSON formats
- Graphical interface support (GUI)
- OR logic between filters
- Regular expression pattern matching
- Fuzzy matching algorithms

## Example Usage

```bash
# List all users in the system
./run list-users

# Find users named John
./run list-users --first John

# Find users with specific email domain
./run list-users --email @gmail.com

# Find specific user by multiple criteria
./run list-users --first John --last Doe --phone 555

# Find user by exact USBC ID
./run list-users --usbc_id 12345

# Complex multi-field search
./run list-users --first Alice --address "Main St" --email alice
```

## Edge Cases

- Empty string filters are ignored (not treated as valid filters)
- No users match the filter criteria → Clean "No users found matching criteria" message
- Database connection failures → Exit code 1 with user-friendly error
- Very large result sets → Handle gracefully with readable output
- Special characters in filter strings → Properly escaped for SQL safety
- Case sensitivity → All string matches are case-insensitive
- Null/None values in database → Handle appropriately in comparisons
- Unicode characters in names/addresses → Support international characters
- SQL injection prevention (via SQLAlchemy ORM parameterized queries)
- Performance with large user databases → Efficient query construction

## Additional Notes

- Filters use logical AND operations exclusively (no OR logic)
- String matching is case-insensitive and supports partial matches
- ID fields require exact matches for precision
- Output should be cleanly formatted for CLI readability using Rich tables
- Command should handle gracefully when database is empty
- All database queries use SQLAlchemy ORM for safety and maintainability
