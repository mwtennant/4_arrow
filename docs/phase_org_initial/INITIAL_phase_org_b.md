# Feature: Edit Organization (phase-org-b)

## One-Sentence Purpose

Enable operators to update basic details of an existing organization.

---

## Requirements

- Implement per CLAUDE.md
  - Python 3.12
  - PEP 8
  - Type hints
  - Pytest testing
  - Architectural layers

### CLI Command

- Add a new CLI command: `edit-organization`
- Command should:

  - Require flag: `--organization-id`
  - Accept updatable fields: `--name`, `--address`, `--phone`, `--email`, `--website`
  - Update only the fields provided
  - Allow no-ops (e.g., editing with no fields does nothing, returns 0)

### Behavior

- Must validate that `organization_id` exists
- If changing name, must ensure new name does not conflict with an existing org (case-insensitive)

### Success Criteria

- Organization is updated in the DB
- If no change is made, the system should still confirm success (no error)

### Error Handling

- If `--organization-id` is missing → Exit code 1, message "Missing organization ID."
- If organization not found → Exit code 2, message "Organization not found."
- If updated name would cause a conflict → Exit code 3, message "Organization name already exists."

### Test Cases

- ✅ Update only the address
- ✅ Update name and email
- ❌ Edit non-existent organization → error
- ❌ Try to rename to an existing name → error
- ✅ Call with no updatable fields → returns success, no changes

---

## Non-goals / Future Ideas

- Creating an org (see phase-org-a)
- Editing roles or permissions (see phase-org-f/g)

---

## Examples Required

- CLI usage updating one field
- CLI usage updating multiple fields
- CLI failure on invalid org ID
- CLI failure on duplicate name

---

## Docs Required

- CLI doc for `edit-organization`
- Example: DB update logic
- Model: Which fields are mutable

---

## Edge Cases

- Update to same values → should not throw error
- Names with mixed casing → validate against existing ones case-insensitively
- Blank string as value → rejected with message "Empty value not allowed"
