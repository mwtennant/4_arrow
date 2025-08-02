# Feature: Create Organization Roles (phase-org-g)

## One-Sentence Purpose

Allow operators to create roles for an organization, optionally assigning default permissions.

---

## Requirements

### CLI Command

- Add new command: `create-org-role`
- Command should:

  - Require `--organization-id`
  - Require `--name` (role name)
  - Optionally accept `--permissions` (comma-separated list of permission names)

### Behavior

- Validate that organization exists
- Validate that role name is unique (case-insensitive)
- Validate that each permission name exists in that organization
- Store the role and link permissions if provided

### Success Criteria

- Role is created with optional default permissions
- Role ID is returned or displayed

### Error Handling

- Missing `--organization-id` or `--name` → Exit code 1
- Org not found → Exit code 2
- Role name already exists → Exit code 3
- Any permission not found → Exit code 4

---

## Test Cases

- ✅ Create role with no permissions
- ✅ Create role with one or more valid permissions
- ❌ Missing role name → error
- ❌ Duplicate role name → error
- ❌ Invalid permission in list → error

---

## Non-goals / Future Ideas

- Editing roles
- Assigning users to roles (see next phase)

---

## Examples Required

- CLI usage with and without permissions
- Conflict on role name or permission

---

## Docs Required

- CLI doc for `create-org-role`
- Role-permission schema reference

---

## Edge Cases

- Comma-separated permissions must be trimmed and case-insensitive
- Roles with no permissions are valid
- Permissions list can be in any order
