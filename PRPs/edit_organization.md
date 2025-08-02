# Product Requirements Prompt: Edit Organization Management (Phase Org-B)

## Summary

Implement an organization editing system for the 4th Arrow Tournament Control application. This feature provides a CLI command to update existing organization details including name, address, phone, email, and website fields with proper validation, conflict detection, and persistence in SQLite database, following established CLAUDE.md conventions.

## Step-by-Step Plan

### Slice 1: CLI Command Implementation

1. Create `edit-organization` command with required `--organization-id` flag (must reference existing org)
2. Implement optional update fields:

   - `--name` (must be unique, case-insensitive)
   - `--address`
   - `--phone`
   - `--email`
   - `--website`

3. Add validation for organization existence and name uniqueness
4. Handle no-op scenarios gracefully (no fields provided still returns success)

### Slice 2: Database Integration

1. Integrate with existing SQLAlchemy `Organization` model in `core/models.py`
2. Implement selective field updates in `tournament_control.db`
3. Use database transactions from `storage/database.py` for consistency
4. Add name conflict detection with case-insensitive matching

### Slice 3: Validation and Testing

1. Write a comprehensive test suite covering all scenarios
2. Ensure ≥85% test coverage
3. Validate edge cases and error conditions
4. Confirm rollback behavior on errors or conflicts

## File List

### Core Implementation Files

- `src/commands/edit_organization.py` – CLI command implementation
- `core/models.py` – SQLAlchemy `Organization` model
- `storage/database.py` – DB connection and transaction layer
- `main.py` – CLI entry point

### Test Files

- `tests/test_edit_organization.py` – Unit tests
- `tests/test_cli.py` – CLI integration tests

### Configuration Files

- `requirements.txt` – Click, SQLAlchemy (existing)

## CLI Interface

### Command Syntax

```bash
# Update one field
python main.py edit-organization --organization-id 1 --name "New Org Name"

# Update multiple fields
python main.py edit-organization --organization-id 1 --name "Updated" --email "new@example.com"

# No-op (success, no changes)
python main.py edit-organization --organization-id 1
```

### Required Arguments

- `--organization-id`: Integer, must point to an existing org

### Optional Arguments

- `--name`: New name (must be unique, case-insensitive)
- `--address`, `--phone`, `--email`, `--website`: Updatable fields

### Exit Codes

- `0`: Success (including no-op)
- `1`: Missing `--organization-id`
- `2`: Org not found
- `3`: Name conflict

### Error Messages

- ID missing: "Missing organization ID."
- Not found: "Organization not found."
- Name conflict: "Organization name already exists."
- Empty fields: "Empty value not allowed."

## Validations

### Input

1. Required `--organization-id`
2. Org ID must resolve to existing record
3. Name must be unique (case-insensitive)
4. Reject empty values
5. Allow no-op if no updates

### Business Rules

1. Selectively update only provided fields
2. Compare names case-insensitively
3. Allow updates to same values
4. Ensure transaction rollback on failure

## Test Coverage Requirements

### Success

- ✅ One field update
- ✅ Multiple fields update
- ✅ Update to same value
- ✅ No-op

### Error Cases

- ❌ Missing ID → Exit 1
- ❌ Org not found → Exit 2
- ❌ Name conflict → Exit 3
- ❌ Empty string → Error message

### Edge Cases

- Case mismatch → detects duplicate
- Whitespace → trims or rejects
- Transaction rollback if error during commit
- Simulate DB connection failure

## Implementation Notes

### CLAUDE.md Compliance

- Python 3.12, PEP8
- Type hints and Google-style docstrings
- pytest for all test coverage
- ≥85% test coverage
- Use `core/` and `storage/` appropriately

### Example CLI

```python
@click.command()
@click.option('--organization-id', required=True, type=int)
@click.option('--name', type=str)
@click.option('--address', type=str)
@click.option('--phone', type=str)
@click.option('--email', type=str)
@click.option('--website', type=str)
def edit_organization(...):
    # Validate inputs
    # Query org by ID
    # Check name conflict
    # Update fields
    # Commit transaction
```

## References

- `PRPs/create_organization.md`
- `core/models.py`
- `tests/test_create_organization.py`
- `CLI_REFERENCE.md` → Add usage example and flag documentation
- Document which fields are mutable in `Organization` model
