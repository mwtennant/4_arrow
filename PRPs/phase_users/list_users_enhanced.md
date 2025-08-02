# Product Requirements Prompt: List Users Enhanced (Phase User‑I)

## Summary

Extend the `list-users` CLI command so operators can quickly filter, sort, page, and export user data. The feature supports role‑based filters, date filters, ordering, paging, and CSV export — all while meeting performance targets for large datasets.

## Step‑by‑Step Plan

| Slice                          | Definition of Done                                                                                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — CLI flags & validation** | Add flags `--role`, `--created-since`, `--order`, `--page-size`, `--csv`; reject invalid enums / bad dates; unit tests for flag parsing.                    |
| **B — Query & Filters**        | SQLAlchemy query builder supports role + date filters, ordering, paging; unit tests validate SQL generated.                                                 |
| **C — Paging & Rich output**   | Default Rich table with zebra‑striping; “Next N remaining…” prompt obeys `page-size`; integration test uses `pexpect`.                                      |
| **D — CSV Export**             | `--csv <path>` writes RFC 4180 file with header `id,name,role,email,created_at`; handles Unicode; detects directory write‑errors (see edge cases).          |
| **E — Performance & Coverage** | Query 10 k users with role filter + CSV export in < 30 s and < 100 MB RSS; composite DB index exists; pytest ≥ 85 % overall, ≥ 95 % on `list_users` module. |

## CLI Interface

```bash
# Role‑filtered listing
./run list-users --role registered_user --order last_name

# Date filter + CSV export with custom page size
./run list-users --created-since 2025-01-01 --page-size 25 --csv reports/active_users.csv
```

### Flags

| Flag              | Values                                                   | Default     | Notes                                |
| ----------------- | -------------------------------------------------------- | ----------- | ------------------------------------ |
| `--role`          | `registered_user` \| `unregistered_user` \| `org_member` | (no filter) | Maps to `ProfileRole` enum.          |
| `--created-since` | `YYYY-MM-DD`                                             | (no filter) | Inclusive date filter.               |
| `--order`         | `id` \| `last_name` \| `created_at`                      | `id`        |                                      |
| `--page-size`     | int > 0                                                  | 50          | Prompts after each page.             |
| `--csv`           | `<path>`                                                 | —           | Writes export instead of Rich table. |

### Exit Codes

| Code | Meaning                                            |
| ---- | -------------------------------------------------- |
| 0    | Success                                            |
| 1    | Unexpected error / DB failure / file‑system error  |
| 4    | Invalid arguments (bad flag value, bad date, etc.) |

## Database Integration

- Uses SQLAlchemy query with **composite index `(role, created_at)`** to guarantee < 30 s performance target.
- Respects soft‑deleted users (`deleted_at IS NULL`).

## Testing & Validation

- Unit tests for flag parsing, filter combinations, paging logic.
- CSV round‑trip test with Unicode names (`José`, `Zoë`).
- Paging test hits **Enter** repeatedly to auto-advance until end.
- Performance test seeds 10 k users and asserts runtime/RSS thresholds.

## File List

| Path                                       | Type                                      |
| ------------------------------------------ | ----------------------------------------- |
| `src/commands/list_users.py`               | **modified**                              |
| `src/commands/__init__.py`                 | **modified** – export `list_users`        |
| `tests/test_list_users.py`                 | **new**                                   |
| `tests/test_cli_list_users.py`             | **new**                                   |
| `utils/csv_writer.py`                      | **new** – shared CSV helper               |
| `migrations/2025_add_role_created_idx.sql` | **new** – adds `(role, created_at)` index |

## Edge Cases

- Filtering on day of DST transition.
- Unicode names render correctly in table **and** CSV.
- `--csv` path points to a **non‑existent directory** → exit 1 with descriptive error.
- Paging prompt behaves when user just presses **Enter** until results exhausted.
- Ctrl‑C during paging returns exit 5 (operator abort) but leaves terminal in clean state.
