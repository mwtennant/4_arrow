# FEATURE: CLI – user_signup_and_auth

## Overview

Implement the simplest end-to-end user management slice:
sign-up + login for members, stored in SQLite, callable from CLI.

## Requirements

- **signup** command
  - required args: --email, --password, --first, --last
  - optional args: --address, --usbc_id, --tnba_id, --phone
  - Store password **hashed** with bcrypt.
  - Duplicate email → error code 1, friendly message.
- **login** command
  - args: --email, --password
  - Validate hash, print “Authenticated as <first last>”.
  - Wrong creds → exit code 1.
- Data persisted in `inventory.db` via SQLAlchemy.
- PEP 8, type hints, Google docstrings.
- Tests: signup, duplicate signup, login success, login fail.
- Coverage ≥ 85 %.

## Non-goals / future

- Contacts, non-members, merging, profile edit.
- GUI flows (will come in Phase N).

## Examples

None for this slice.

## Docs

- https://pypi.org/project/bcrypt/
- SQLAlchemy quickstart

## Edge cases

- Empty email or password.
- Email lacking “@”.
