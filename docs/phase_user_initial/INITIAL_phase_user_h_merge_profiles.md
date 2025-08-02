# Product Requirements Prompt: Merge Profiles Management (Phase User-H)

## Summary

Implement a flexible CLI command `merge` that allows operators to consolidate duplicate or overlapping user profiles so that all historical data (scores, brackets, org‑membership, etc.) survives under a single _primary_ user ID. The feature applies **within the current database across all organisations**; cross‑organisation merges remain out of scope for Phase 1.

## Step‑by‑Step Plan

| Slice                                                | Definition of Done                                                                                                                                                                                 |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — Identifier & validation**                      | `merge` command accepts `--main-id <int>` and one or more `--merge-id <int>` flags; rejects self‑merge; validates IDs exist; unit tests cover happy path and validation errors.                    |
| **B — Dry‑run mode**                                 | `--dry-run` flag prints a coloured diff table and exits with code 0 without mutating the DB; integration test asserts no DB writes when flag present.                                              |
| **C — Logging**                                      | Each successful merge appends one JSON line to `logs/merge_profile.log` that conforms to the schema below; tests validate schema using `jsonschema`.                                               |
| **D — Interactive conflict resolution & CLI polish** | Interactive prompts handle each conflicting field; non‑interactive modes `--prefer-main` / `--prefer-merge` / `--prefer-longest` resolve automatically; rich help text and short flags `-m`, `-i`. |
| **E — Tests & coverage**                             | Pytest suite ≥ 85 % total coverage and ≥ 90 % on `src/commands/merge.py`; parametrised tests for edge cases; CLI integration tests with `pexpect`.                                                 |

## Technical Requirements

### CLI Interface

```bash
# Merge one duplicate into primary
./run merge --main-id 3 --merge-id 5

# Merge many duplicates at once, dry‑run first
./run merge -m 3 -i 5 -i 11 --dry-run --prefer-main
```

#### Exit codes

| Code | Meaning                                                      |
| ---- | ------------------------------------------------------------ |
| 0    | Success                                                      |
| 1    | Unexpected error / DB failure                                |
| 2    | Duplicate email conflict when `--no-interactive`             |
| 4    | Invalid arguments (missing IDs, self‑merge, non‑existent ID) |
| 5    | Merge aborted by operator (Ctrl‑C or `n` at confirmation)    |

### Logging schema (`logs/merge_profile.log`, JSONL)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MergeProfileEvent",
  "type": "object",
  "required": [
    "event",
    "timestamp",
    "primary_id",
    "merged_ids",
    "field_resolutions"
  ],
  "properties": {
    "event": { "const": "MERGE_PROFILE" },
    "timestamp": { "type": "string", "format": "date-time" },
    "primary_id": { "type": "integer" },
    "merged_ids": { "type": "array", "items": { "type": "integer" } },
    "field_resolutions": {
      "type": "object",
      "additionalProperties": {
        "enum": ["kept_primary", "kept_duplicate", "kept_longest"]
      }
    }
  }
}
```

### Database Integration

- Operates inside a single SQLAlchemy transaction (`session.begin()` or `async with session.begin()`).
- Uses `SELECT … FOR UPDATE` to lock all affected `User` rows.
- Updates FK references in **scores, brackets, org_memberships, transactions** tables.
- Deletes duplicate rows with `soft_delete = True` (sets `deleted_at` timestamp).
- `scripts/add_unique_indexes.sql` adds composite unique index on `(email, phone)`.

### Conflict‑resolution rules

1. If one value is `NULL` / empty and the other non‑empty → keep non‑empty.
2. When both non‑null but different:

   - In interactive mode → prompt operator.
   - If `--prefer-main` or `--prefer-merge` present → honour flag.
   - If `--prefer-longest` present → keep longer string / newer `updated_at`.

### Testing & Validation

- Unit tests covering each slice plus negative paths.
- Integration test merging 50 users into one to measure runtime < 5 s.
- Contract test to ensure JSON log lines validate against schema.

## File List

| Path                             | Type                                                |
| -------------------------------- | --------------------------------------------------- |
| `src/commands/merge.py`          | **new**                                             |
| `src/commands/__init__.py`       | **modified** – export `merge`                       |
| `core/models.py`                 | **modified** – add `deleted_at`, helper soft‑delete |
| `storage/database.py`            | **modified** – add `get_session()` util             |
| `scripts/add_unique_indexes.sql` | **new**                                             |
| `tests/test_merge_profiles.py`   | **new**                                             |
| `tests/test_cli_merge.py`        | **new**                                             |
| `logs/`                          | directory, created by CLI                           |

## Edge Cases

- Merging IDs that share both `USBC_ID` and `TNBA_ID` but have diverging names.
- Attempts across different organisations (reject with exit 4).
- Operator abort mid‑prompt or Ctrl‑C ensures complete rollback.
- Large batch merge performance & memory footprint.
