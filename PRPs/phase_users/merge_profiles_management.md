# Product Requirements Prompt: Merge Profiles Management (Phase User-H)

## Summary

Implement a robust `merge` CLI command that consolidates duplicate user profiles **within the current database**. The command updates all foreign‑key references so historical data (scores, brackets, organisation memberships, transactions) survives under a single primary ID. Cross‑organisation merges remain out‑of‑scope for this phase.

## Step‑by‑Step Plan

| Slice                                    | Definition of Done                                                                                                                                                                             |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — Identifier & Validation**          | `merge` accepts `--main-id <int>` and one or more `--merge-id <int>` arguments; rejects self‑merge and invalid/non‑existent IDs; unit tests cover happy & error paths.                         |
| **B — Dry‑Run Mode**                     | `--dry-run` prints a coloured side‑by‑side diff table and exits **0** without DB writes. Integration test asserts no mutations when flag present.                                              |
| **C — Logging**                          | Each successful merge appends a JSON line to `logs/merge_profile.log` conforming to the schema below; tests validate against `jsonschema`.                                                     |
| **D — Conflict Resolution & CLI Polish** | Interactive prompt for each conflicting field _unless_ operator passes `--prefer-main`, `--prefer-merge`, or `--prefer-longest`. Rich help text plus short flags `-m` (main) and `-i` (merge). |
| **E — Tests & Coverage**                 | Pytest suite ≥ 85 % overall and ≥ 90 % on `src/commands/merge.py`; parametrised edge‑case tests; CLI integration tests via `pexpect`; batch‑merge perf test (50→1) completes < 5 s.            |

### CLI Usage Examples

```bash
# Merge a single duplicate into primary
./run merge --main-id 3 --merge-id 5

# Merge many duplicates, dry‑run first and auto‑prefer main values
./run merge -m 3 -i 5 -i 11 --dry-run --prefer-main
```

#### Exit Codes

| Code  | Meaning                                                      |
| ----- | ------------------------------------------------------------ |
| **0** | Success                                                      |
| **1** | Unexpected error / DB failure                                |
| **2** | Duplicate‑email conflict when `--no-interactive`             |
| **4** | Invalid arguments (missing IDs, self‑merge, non‑existent ID) |
| **5** | Operator aborted (Ctrl‑C or `n` at final confirmation)       |

### Logging Schema (JSON Lines)

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

- Uses **synchronous** SQLAlchemy session (`with Session.begin():`) and `SELECT ... FOR UPDATE` to lock affected rows.
- Updates FK references in `scores`, `brackets`, `org_memberships`, `transactions` tables.
- Soft‑deletes duplicates (`deleted_at` timestamp).
- `scripts/add_unique_indexes.sql` adds composite unique index on `(email, phone)`.

### Conflict‑Resolution Rules

1. If one value is **NULL/empty** and the other non‑empty → keep non‑empty.
2. If **both values NULL/empty** → leave NULL (no prompt required).
3. If both non‑null but different →

   - Interactive mode: prompt operator.
   - `--prefer-main` / `--prefer-merge` / `--prefer-longest` auto‑select.

### File List

| Path                             | Type                                                |
| -------------------------------- | --------------------------------------------------- |
| `src/commands/merge.py`          | **new**                                             |
| `src/commands/__init__.py`       | **modified** – export `merge`                       |
| `core/models.py`                 | **modified** – add `deleted_at`, soft‑delete helper |
| `storage/database.py`            | **modified** – add `get_session()`                  |
| `scripts/add_unique_indexes.sql` | **new**                                             |
| `tests/test_merge_profiles.py`   | **new**                                             |
| `tests/test_cli_merge.py`        | **new**                                             |
| `logs/`                          | **runtime directory**                               |

### Edge Cases

- Duplicate IDs share both `USBC_ID` and `TNBA_ID` yet names diverge.
- Attempted merge across different organisations → exit 4.
- Operator abort via prompt timeout or Ctrl‑C triggers full rollback.
- Merging 50+ IDs in one call must remain < 5 s and < 100 MB RSS.
