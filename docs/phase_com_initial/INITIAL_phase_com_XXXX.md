# Feature: Contact Members of an Organization (phase-comm-XXXX)

## One-Sentence Purpose

Enable operators to list contact information for members of a given organization.

---

## Requirements

### CLI Command

- Add new command: `contact-members`
- Command should:
  - Require `--organization-id`
  - Support optional filters: `--role`, `--registered-only`, `--unregistered-only`
  - Output member contact data in a readable table (using Rich)

### Output Columns

- `User ID`
- `Name`
- `Email`
- `Phone`
- `Role`
- `Registered?` (yes/no)

### Behavior

- Must validate that organization exists
- Return list of all users in org with known contact details
- If filtered by role or user type, respect those constraints

### Success Criteria

- CLI outputs readable list of org members with usable contact data
- Filters work independently or in combination

### Error Handling

- If org not found → Exit code 2
- If invalid role specified → Exit code 3
- If no contacts match → Exit 0 with message "No matching members"

---

## Test Cases

- ✅ List all members (default)
- ✅ Filter by role
- ✅ Filter by registered/unregistered
- ❌ Nonexistent org → error
- ❌ Invalid role → error
- ✅ No matches → empty table + message

---

## Non-goals / Future Ideas

- Actually sending messages (email/sms)
- Exporting to CSV or PDF

---

## Examples Required

- CLI usage with and without filters
- CLI output sample (Rich table)

---

## Docs Required

- CLI doc for `contact-members`
- Reference list of standard roles

---

## Edge Cases

- Users with no email/phone → show empty string
- Role filters should be case-insensitive
- Mixed roles in org → supported
