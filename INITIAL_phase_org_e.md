# Feature: Remove User from Organization (phase-org-e)

## One-Sentence Purpose

Allow operators to remove one or more users from an organization using their user ID.

---

## Requirements

### CLI Command

- Add CLI command: `remove-org-user`
- Command should:

  - Require `--organization-id`
  - Accept one or more `--user-id` flags (or a comma-separated list)
  - Optionally require `--force` for destructive batch actions (future-compatible)

### Behavior

- Validate that organization exists (Exit 2)
- Validate each `user_id` exists in the organization’s membership list
- For each valid membership, remove the user
- For users not in org, skip and log warning
- No hard error for skipped users

### Success Criteria

- Users are cleanly removed from the org
- Skipped users do not halt execution
- Exit with success if at least one operation completes or is skipped

### Error Handling

- Exit 1 → Missing required args (e.g., no user IDs or org ID)
- Exit 2 → Organization not found
- Exit 5 → No user IDs provided (or all were invalid syntax)

---

## Test Cases

- ✅ Remove one valid user from org
- ✅ Remove multiple users (some valid, some not in org)
- ✅ Repeated `--user-id` values de-duped
- ❌ Org ID not provided → Exit 1
- ❌ Org ID invalid → Exit 2
- ❌ No users provided → Exit 5

---

## Non-goals / Future Ideas

- Batch confirmation for large removals
- Support removing users by email or role
- Remove all members from org

---

## Examples Required

- CLI: single user removal
- CLI: multiple users, some valid, some skipped
- Error output: missing org ID, no users

---

## Docs Required

- CLI doc for `remove-org-user`
- Reference to `OrganizationMembership` table

---

## Edge Cases

- Duplicate `--user-id` entries → silently de-dupe
- User not in org → log warning, skip
- Organization with no users → command should still validate and exit cleanly

---

## Required Models

- `OrganizationMembership(user_id, organization_id, role_id)`
