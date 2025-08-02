# Feature: Create Organization (phase-org-a)

## One-Sentence Purpose

Allow operators to create a new organization, specifying core identifying information.

---

## Requirements

### CLI Command

- Add a new CLI command: `create-organization`
- Command should:

  - Accept required flags: `--name`, `--address`
  - Validate that the name is not already taken
  - Create and persist a new `Organization` record
  - Return the `organization_id` on success

### Fields

- Required:

  - `name` (str)
  - `address` (str)

- Optional (but prepare schema for future support):

  - `phone` (str)
  - `email` (str)
  - `website` (str)

### Success Criteria

- Org is stored in database and retrievable via `get-organization` (future slice)
- Organization name is unique (case-insensitive)
- Operator receives success confirmation + org ID

### Error Handling

- If `--name` or `--address` is missing → Exit code 1, message "Missing required field."
- If duplicate org name (case-insensitive) → Exit code 2, message "Organization with this name already exists."

### Test Cases

- ✅ Create with valid input → succeeds and prints org ID
- ❌ Create with no name → fails with exit code 1
- ❌ Create with duplicate name → fails with exit code 2
- ✅ Create with name differing only in case → fails

---

## Non-goals / Future Ideas

- Editing orgs (see phase-org-b)
- Role or permission setup (see phase-org-f/g)
- Linking users to orgs (see phase-org-c)

---

## Examples Required

- CLI usage for successful creation
- CLI error for missing field
- CLI error for duplicate name

---

## Docs Required

- Example output for success and errors
- CLI doc for `create-organization`
- Model doc for `Organization`

---

## Edge Cases

- Org name with extra spaces or mixed case → treated as duplicate
- Long names or addresses → must be truncated or validated (TBD length limits)
- Multi-word names → support quoted strings in CLI
