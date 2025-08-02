# Feature: Create Organization Permissions (phase-org-f)

## One-Sentence Purpose

Define organization-level permissions that can later be assigned to roles.

---

## Requirements

### CLI Command

- Add new command: `create-org-permission`
- Command should:

  - Require `--organization-id`
  - Require `--name` (permission name, case-insensitive uniqueness within org)
  - Optionally accept `--description`

### Behavior

- Validate that organization exists (Exit 2)
- Validate that permission name is unique (case-insensitive) within the org (Exit 3)
- Validate name/description length (e.g. name ≤ 64 chars, description ≤ 255 chars)
- Store new permission and return its ID on success

### Success Criteria

- Permission is created and stored
- Duplicate names are rejected
- Description may be empty

### Error Handling

- Exit 1 → Missing required arguments (`--organization-id` or `--name`)
- Exit 2 → Organization not found
- Exit 3 → Duplicate permission name in org

---

## Test Cases

- ✅ Create permission with name only
- ✅ Create permission with name + description
- ❌ Create duplicate permission in same org → Exit 3
- ❌ Name exceeds max length → validation failure

---

## Non-goals / Future Ideas

- Assigning permissions to roles (phase-org-f)
- Editing or deleting permissions
- Permission templates or defaults per org type

---

## Examples Required

- CLI: creating one permission
- CLI: permission with long description
- CLI: rejection on duplicate name

---

## Docs Required

- CLI doc for `create-org-permission`
- Model doc for `Permission(name, description, organization_id)`

---

## Edge Cases

- Mixed case duplicate ("Create Tournament" vs "create tournament") → reject
- Empty string for description → allowed
- Special characters in name → validate as needed (e.g. alphanum + dash)

---

## Required Models

- `Permission(id, name, description, organization_id)`
