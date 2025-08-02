# FEATURE: CLI – merge_profiles (Phase User-D)

## Overview

Create a flexible CLI to merge user profiles in the system.  
This tool helps resolve duplicate or overlapping records. The user with the most complete profile will be the “main” record, while others will be merged into it.  
If conflicting fields exist (e.g. different phone numbers or addresses), the CLI should prompt the operator to choose which value to keep.  
All merged references (like scores, tournament history, etc.) must eventually point to the main user.

## Requirements

- CLI command: `merge`
  - Required args:
    - `--main-id` (ID of the primary user)
    - One or more `--merge-id` arguments (IDs to be merged into `main-id`)
  - If conflicting data is found (e.g. different addresses), prompt the user to choose the correct value
  - Must detect and reject invalid IDs (exit code 4)
  - Support merging multiple IDs in a single call
- Merge must preserve:
  - All valid user data (choosing the most complete field set)
  - User relationships (e.g. tournament entries, scores – tracked for future phase)
- Data persisted in `inventory.db` via SQLAlchemy ORM
- Follow PEP 8, use type hints, and Google-style docstrings
- Code lives in: `src/commands/merge.py`
- Tests live in: `tests/test_merge_profiles.py`

## Tests Required

- ✅ Merge a single user into a main user
- ✅ Merge multiple users into one main user
- 🚫 Invalid or non-existent `--main-id` or `--merge-id` → exit code 4
- 🚫 Empty or missing `--main-id`
- ✅ Merge two users with conflicting fields, prompt and preserve selected values
- ✅ Ensure merged user history would point to correct user-id (optional, future test)

## Code Coverage

- Target: ≥ 85%

## Non-goals / Future

- Rewriting related history (scores, tournaments, etc.) – handled in Phase X
- Manual profile field editing
- GUI-based merging

## Examples

```bash
# Merge one user into another
./run merge --main-id 3 --merge-id 5

# Merge multiple users into a main profile
./run merge --main-id 3 --merge-id 5 --merge-id 11
```

## Docs

- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://click.palletsprojects.com/ – for CLI argument parsing
- CLAUDE.md – for project code style, test coverage, and structure

## Edge Cases

- Missing or empty `--main-id`
- Invalid or non-existent user ID(s)
- Conflicting field values (e.g. address, phone) must be resolved interactively
- Attempt to merge a user into themselves

## Final Notes

- Summary:

  - Successfully implemented merge profiles feature per PRP specifications
  - Created CLI command supporting single and multiple user merges
  - Implemented interactive conflict resolution for overlapping field values
  - Added proper error handling with exit codes (4 for validation errors, 1 for
    database errors)
  - Achieved 100% test coverage for merge module and 96% overall coverage
  - Validated functionality with manual testing including conflict resolution
    and error cases
  - All tests pass (109/109) and coverage exceeds 85% requirement

  CLI_REFERENCE.md has been updated with comprehensive documentation for the
  new merge command, including:

  - Complete syntax and required options
  - Multiple examples (single and multi-user merges)
  - Detailed interactive conflict resolution workflow
  - All error cases with exit codes
  - User cancellation options
  - Merge behavior explanation
  - Added exit code 4 to the exit codes section
  - New "Merge Duplicate Profiles" workflow section

  The documentation provides users with everything they need to understand and
  use the merge functionality effectively.

### Changed files

- src/commands/merge.py - Created merge profiles command implementation with
  interactive conflict resolution
- main.py - Added merge command to CLI interface
- tests/test_merge_profiles.py - Created comprehensive test suite with 100%
  coverage
