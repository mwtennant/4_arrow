# Product Requirements Prompt: Edit-Profile Management (Slice 1-B)

## Summary

Add profile-management commands (get, edit, delete) to the existing 4th Arrow CLI while leaving signup/login untouched.  
Scope: CLI only, Rich table output, SQLite persistence via SQLAlchemy.

---

## Step-by-Step Plan

| Phase                     | Tasks                                                                                                                                          | Files                    |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| **1 – Profile Retrieval** | • `get-profile` command with exactly **one** id flag.<br>• Use Rich table (border=MINIMAL) for display.<br>• “ERROR: No user found.” → exit 1. | core/profile.py, main.py |
| **2 – Profile Editing**   | • `edit-profile` command.<br>• Validate at least one field, no empty strings.<br>• Email field immutable.                                      | core/profile.py, tests   |
| **3 – Profile Deletion**  | • `delete-profile` with `--confirm yes` flag.<br>• Reject if missing/invalid.<br>• “ERROR: Deletion aborted.” → exit 1.                        | core/profile.py, tests   |
| **4 – Validation**        | • Extend tests.<br>• Run full suite, ensure ≥ 85 % coverage.<br>• All existing auth tests must still pass.                                     | tests/                   |

---

## File List

**Core / CLI**

- main.py ← extend Click group with new sub-commands
- core/profile.py ← new helpers: get_profile, edit_profile, delete_profile
- core/models.py  ← no schema change (reuse `User`)
- core/**init**.py ← only if missing

**Tests**

- tests/test_profile.py unit tests for core functions
- tests/test_cli.py   extend with new CLI cases

**Config / deps**

- requirements.txt  ← add `rich`

---

## CLI Interface (examples)

    # Get profile (one id flag required)
    python main.py get-profile --user-id 123
    python main.py get-profile --email alice@example.com
    python main.py get-profile --usbc-id 555555
    python main.py get-profile --tnba-id 98765

    # Edit profile (at least one field)
    python main.py edit-profile --user-id 123 --first Alice --phone 555-1234

    # Delete profile (confirmation required)
    python main.py delete-profile --user-id 123 --confirm yes

---

## Output & Error Format

| Command        | Success output                                                                                                 | Failure output             |
| -------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------- |
| get-profile    | Rich table (border=MINIMAL) with columns: user_id · first · last · email · phone · address · usbc_id · tnba_id | `ERROR: No user found.`    |
| edit-profile   | `Profile updated.`                                                                                             | `ERROR: <reason>`          |
| delete-profile | `Profile deleted.`                                                                                             | `ERROR: Deletion aborted.` |

_All error lines begin with **“ERROR:”** so tests can assert on the prefix._

---

## Tests (pytest expectations)

| Scenario                         | Exit code |
| -------------------------------- | --------- |
| get by user-id                   | 0         |
| get by email                     | 0         |
| get by usbc-id                   | 0         |
| get by tnba-id                   | 0         |
| get with two id flags            | 1         |
| get non-existent                 | 1         |
| edit-profile success             | 0         |
| edit-profile invalid user        | 1         |
| edit-profile empty string field  | 1         |
| edit-profile with no fields      | 1         |
| edit-profile email attempt       | 1         |
| delete-profile success (confirm) | 0         |
| delete-profile without confirm   | 1         |
| delete-profile non-existent user | 1         |

Coverage goal: **≥ 85 %** overall.

---

## References

- Rich tables: https://pypi.org/project/rich/
- SQLAlchemy sessions: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- Click framework: https://click.palletsprojects.com/

---

## Success Criteria

1. Commands behave per specs & error table.
2. Existing signup/login tests still pass.
3. Coverage ≥ 85 %.
4. Email field remains immutable.
5. Error prefix `ERROR:` used consistently.
6. Code follows CLAUDE.md standards.

---

## Non-Goals

- Editing via email (future slice)
- Profile avatars, audit trail, or GUI flows
