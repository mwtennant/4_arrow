# Product Requirements Prompt: Merge Profiles Management (Phase User-H)

## Summary

Implement a flexible CLI command to merge user profiles in the 4th Arrow Tournament Control system. This tool resolves duplicate or overlapping user records by merging one or more profiles into a designated main profile. The system must preserve all valid data, resolve conflicting fields through interactive prompts, and maintain full referential integrity by redirecting all foreign key references to the merged user ID.

## Step-by-Step Plan

### Phase User: CLI Command

1. Add `merge` command with required args: `--main-id`, `--merge-id`
2. Validate user ID formats and existence
3. Support multiple `--merge-id` inputs in a single call
4. Prevent merging a user into themselves

### Phase 2: Merge Logic

1. Compare all mergeable fields to detect conflicts
2. Use interactive prompts to resolve conflicts
3. Prefer more complete data when no conflict exists
4. Handle empty/null values with fallback logic

### Phase 3: Database Integration

1. Use SQLAlchemy models for query/update
2. Wrap merge logic in a DB transaction
3. Delete merged user(s) after updating all references
4. Ensure referential integrity for linked tables

### Phase 4: Tests & Validation

1. Write test suite: single/multi-user merges, conflicts, edge cases
2. Mock input for interactive prompt resolution
3. Confirm proper cleanup and persistence
4. Reach minimum 85% coverage threshold

## File List

### Core Implementation

- `src/commands/merge.py` – Merge command logic
- `core/models.py` – Existing User model
- `storage/database.py` – DB session helper
- `main.py` – Register `merge` in CLI

### Test Files

- `tests/test_merge_profiles.py` – Unit tests for merge logic
- `tests/test_cli.py` – CLI integration test

## CLI Interface

### Usage

```bash
# Merge a single profile
./run merge --main-id 3 --merge-id 5

# Merge multiple profiles
./run merge --main-id 3 --merge-id 5 --merge-id 11
```

## Interactive Conflict Resolution

When conflicting field values are detected, the system will:

1. Display both values clearly with their respective user IDs
2. Present options:
   - `1` — Keep the main user's value
   - `2` — Keep the merge user's value
   - `s` — Skip this field (leave main's value unchanged)
3. Repeat this prompt for each conflicting field
4. Show a summary of selected changes before committing
5. Prompt the user for confirmation before finalizing the merge
6. Allow user to abort at any time by entering `n` or Ctrl+C

### Example Conflict Resolution Flow

```
Conflicting phone numbers found:
Main user (ID 3): 555-1234
Merge user (ID 5): 555-5678
Choose which value to keep [1=main, 2=merge, s=skip]: 1

Conflicting addresses found:
Main user (ID 3): 123 Main St
Merge user (ID 5): 456 Oak Ave
Choose which value to keep [1=main, 2=merge, s=skip]: 2

Summary of changes:
- Phone: Keeping main user value (555-1234)
- Address: Using merge user value (456 Oak Ave)

Proceed with merge? [y/N]: y
Profile merge completed successfully.
```

## Example Usage

```bash
# Simple merge operation
./run merge --main-id 3 --merge-id 5

# Multi-user merge
./run merge --main-id 3 --merge-id 5 --merge-id 11

# Expected interactive session:
./run merge --main-id 3 --merge-id 5
# Merging user 5 into user 3...
# Conflicting phone numbers found:
# Main user (ID 3): 555-1234
# Merge user (ID 5): 555-5678
# Choose which value to keep [1=main, 2=merge, s=skip]: 1
# Profile merge completed successfully.
```

## Edge Cases

- Empty string for `--main-id` → Exit code 4
- Invalid or non-existent user IDs → Exit code 4, descriptive error message
- Attempt to merge user into themselves → Exit code 4, descriptive error message
- Database connection failures → Exit code 1, user-friendly error message
- Unique constraint violations (email) → Handle gracefully with conflict resolution
- Null/empty field handling during merge operations
- Transaction rollback on merge failure
- Multiple conflicting fields requiring sequential resolution
- User cancellation during interactive prompts
