# Product Requirements Prompt: Role Terminology Refactor

## Summary

Replace legacy `member / non-member` terminology with standardized roles: `registered_user`, `unregistered_user`, and `org_member` across code, tests, and documentation.

## Requirements

- Add `ProfileRole` **Enum** with values `REGISTERED_USER`, `UNREGISTERED_USER`, `ORG_MEMBER`.
- In `User` model add boolean accessors:

  - `is_registered_user` (`role == REGISTERED_USER`)
  - `is_unregistered_user` (`role == UNREGISTERED_USER`)
  - `is_org_member` (`role == ORG_MEMBER`)

- Deprecate `is_member`; keep a property that raises `DeprecationWarning` on first access.
- **CLI flags**: replace `--member` with `--registered-user`; update help strings and README examples.
- Migrate all fixtures and tests to use new enum values and boolean helpers.
- Provide a one‑off migration script updating existing DB rows (`ROLE='MEMBER' → 'REGISTERED_USER'`, etc.).
- Add **unit test** that asserts no identifier `member` remains in import paths or attribute names (regex guard).

## Non‑Goals

- GUI terminology update (handled automatically once models and flags change).

## Docs Required

- Create ADR 008 “Role Terminology Migration”.
- Changelog entry describing breaking change and migration steps.

## Edge‑Cases

- Legacy JSON export files consumed by external systems → provide import shim translating old keys.
- Third‑party integrations still expecting `is_member` flag → document DeprecationWarning mechanism.
