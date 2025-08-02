# FEATURE: CLI – list_users (Phase User-E)

## Summary

Implement a CLI command to retrieve all user profiles in the system with optional filters. This tool supports flexible search by allowing operators to apply zero or multiple filters to narrow down results.

## Requirements

- CLI command: `list-users`
  - Optional arguments:
    - `--first`
    - `--last`
    - `--address`
    - `--usbc_id`
    - `--tnba_id`
    - `--phone`
    - `--email`
- Data must be queried from `inventory.db` via SQLAlchemy ORM
- Conform to:
  - PEP 8 formatting
  - Type hints throughout
  - Google-style docstrings
- File locations:
  - Implementation: `src/commands/list_users.py`
  - Tests: `tests/list_users.py`

## Tests Required

- ✅ Returns all users when no filters are applied
- ✅ Returns correct subset with each individual filter (test each)
- ✅ Returns correct subset when multiple filters (but not all) are applied
- ✅ Returns correct subset when all filters are applied
- ✅ Returns empty result when no users match the filter (Edge Case)

## Code Coverage

- Required: ≥ 85%

## Non-goals / Future Work

- Filtering by:
  - Tournament participation
  - Organization membership
  - Scoring data (high/low games, averages, etc.)
- Graphical interface support (GUI)

## Example Usage

```bash
# List all users
./run list-users

# Filter by first name
./run list-users --first John

# Filter by multiple fields
./run list-users --first John --email john@example.com
```

## Docs Required

- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://click.palletsprojects.com/ – CLI argument parsing
- CLAUDE.md – project-wide rules for style, structure, and coverage

## Edge Cases

- Return clean, well-formatted output when no users match
- Handle DB connection failure (optional if shared globally)
- Silent fail on unrecognized filters (optional future feature)

## Extra Notes

Ensure filters are combined with logical `AND` operations (not `OR`). Output should be cleanly formatted for CLI readability using Rich or similar.

## Final Notes

Update Todos
⎿ ☒ Read PRP file and understand requirements  
 ☒ Examine existing codebase structure
☒ Create src/commands/list_users.py implementation
☒ Update main.py to include list-users command
☒ Create tests/test_list_users.py
☒ Run tests and ensure 85% coverage
☒ Fix any issues until validations pass

⏺ Done ✅

Successfully implemented the list-users command according to the PRP specifications. Here
are the changed files:

New Files Created:

- src/commands/list_users.py - Core implementation with filtering logic and Rich table
  display

  - tests/test_list_users.py - Comprehensive test suite with 21 tests covering all scenarios

  Modified Files:

  - main.py - Added the list-users CLI command with all filter options

  Key Features Implemented:
  ✅ CLI command list-users with optional filter arguments (--first, --last, --email, --phone,
  --address, --usbc_id, --tnba_id)
  ✅ Dynamic query building with logical AND operations for multiple filters
  ✅ Partial matching for string fields, exact matching for ID fields
  ✅ Rich table output with proper formatting
  ✅ Empty result handling with clean messaging
  ✅ Error handling for database failures
  ✅ 100% test coverage (exceeding the 85% requirement)
  ✅ All 21 tests passing
  ✅ PEP 8 compliance with type hints and Google-style docstrings

  The implementation follows all project conventions and integrates seamlessly with the
  existing codebase architecture.

  Perfect! ✅ The CLI_REFERENCE.md documentation has now been updated with comprehensive
  documentation for the list-users command. The documentation includes:

  📖 Complete Documentation Added:

  - Syntax: Full command syntax with all optional parameters
  - Filter Options: Detailed explanation of all 7 filter parameters
  - Filter Behavior: Clear distinction between partial and exact matching
  - Examples: 12 comprehensive examples covering all use cases
  - Sample Output: Rich table format example with actual output
  - Error Handling: Database and unexpected error cases
  - Use Cases: Practical scenarios for using the command
  - Workflow Section: New "User Search and Listing" workflow with 15 practical examples

  🎯 Key Features Documented:

  - All filter parameters (--first, --last, --email, --phone, --address, --usbc_id, --tnba_id)
  - Partial matching for string fields vs exact matching for ID fields
  - AND logic for multiple filters
  - Rich table output formatting
  - Empty result handling
  - Error cases with exit codes

  The documentation is now complete and provides users with everything they need to
  effectively use the flexible filtering capabilities of the list-users command!
