# Product Requirements Prompt: Role Terminology Refactor (Phase User‑J)

## Summary

Standardise all user‑role terminology across 4th Arrow Tournament Control by replacing legacy **member / non‑member** wording with three explicit roles:

- **`registered_user`** – users who created their own account (have email/password)
- **`unregistered_user`** – users added by an operator but who have not signed up yet
- **`org_member`** – registered users who belong to an organization

The refactor touches models, CLI flags, tests, migration scripts, and docs while maintaining backward compatibility (DeprecationWarnings) during a grace period.

---

## Step‑by‑Step Plan

| Slice                        | Definition of Done                                                                                                                                                                                                                 |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — Core Model & Enum**    | _ProfileRole_ enum expanded; `User` model gains boolean helpers `is_registered_user`, `is_unregistered_user`, `is_org_member`; legacy `is_member` property issues DeprecationWarning. Unit tests assert helpers + warning trigger. |
| **B — CLI Flag Migration**   | Every CLI command replaces `--member` with `--registered-user`. Help text & README examples updated. A shim parses `--member`, maps to new flag, emits DeprecationWarning. CLI integration tests via _pexpect_ pass.               |
| **C — Test‑Suite Migration** | All fixtures & assertions updated; regex guard test fails build if `is_member` appears in non‑legacy paths. Coverage ≥ 85 % overall, ≥ 95 % on role helpers.                                                                       |
| **D — DB Migration & Shim**  | Alembic (or raw SQL) script copies legacy `is_member` boolean into new `role` column, backfills values, adds `CHECK(role IN …)`. JSON import/export shim translates fields for external systems. Round‑trip tests verify fidelity. |
| **E — Docs & Cleanup**       | ADR‑008 written; README, CLI help, and API docs updated. Cleanup task scheduled (Phase 2) to remove shims after 90 days.                                                                                                           |

---

## CLI Impact

### New flag pattern

```bash
# List only registered users
./run list-users --role registered_user

# Legacy flag (accepted, warns, maps to registered_user)
./run list-users --member
```

### Exit Codes

| Code  | Meaning                                                        |
| ----- | -------------------------------------------------------------- |
| **0** | Success                                                        |
| **1** | Unexpected error / DB failure                                  |
| **4** | Invalid arguments (unknown role value, both --role & --member) |

---

## Database Integration

- **Schema** – New `role VARCHAR(32)` column on `users` table; NOT NULL; default `'registered_user'` for fresh sign‑ups.
- **Index** – Composite `(role, created_at)` to keep list‑users performance after filters.
- **Migration script** –

  1. Add column with default `'registered_user'`.
  2. Update existing rows: `role = 'registered_user' IF is_member = TRUE ELSE 'unregistered_user'`.
  3. Drop `is_member` column **after** application code stops reading it (Phase 2).

---

## File List

| Path                                  | Type         | Notes                                 |
| ------------------------------------- | ------------ | ------------------------------------- |
| `core/models.py`                      | **modified** | Add enum + helpers + deprecation shim |
| `src/commands/*`                      | **modified** | Replace `--member` flag, update help  |
| `scripts/migrate_role_terminology.py` | **new**      | Alembic/raw SQL migration             |
| `utils/legacy_shim.py`                | **new**      | JSON field mapper (export/import)     |
| `tests/test_role_helpers.py`          | **new**      | Unit tests for helpers + warning      |
| `tests/test_cli_role_flags.py`        | **new**      | Legacy/new flag behaviour             |
| `docs/ADR‑008‑role‑terminology.md`    | **new**      | Decision record                       |
| existing tests                        | **modified** | Search‑replace terminology            |

---

## Edge Cases & Error‑Handling

- **Partial migration states** – application can read either `role` or legacy flag during grace period.
- **Mixed versions** – deprecation shim avoids breaking older external scripts while new code runs.
- **Third‑party JSON** – legacy keys `is_member` translated on import/export via `utils/legacy_shim.py`.
- **Performance** – helper properties must remain O(1); migration script must process 100 k users < 60 s.
- **Deprecation‑warning fatigue** – warnings filtered to once per process per call‑site.

---

## Validation Targets

1. **Unit + integration tests pass** with coverage thresholds.
2. **Regex guard** (`git grep -n '\bis_member\b'`) finds zero matches outside shim/tests.
3. Migration script reversible (`downgrade`) and idempotent on already‑migrated DB.
4. External JSON export → import round‑trip returns identical dataset.
5. GUI & API endpoints inherit new terminology automatically (via model changes) – manual smoke test.

---

## Success Criteria

- Codebase free of legacy terminology (except shims).
- CLI & tests rely solely on new `--role` parameter and enum helpers.
- Databases migrated with preserved FK relations, <½ second added latency per query.
- Documentation, ADR, and migration guide delivered.
