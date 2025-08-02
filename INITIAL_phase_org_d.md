# Feature: Add User to Organization (phase-org-d)

## One-Sentence Purpose

Allow operators to assign existing users (registered or unregistered) to an organization with an optional role.

---

## Requirements

### CLI Command

- Add CLI command: `add-org-user`
- Command should:

  - Require `--organization-id`
  - Accept one or more `--user-id` values (can be passed multiple times)
  - Optionally accept `--role` (if not provided, user is assigned without a role or with default fallback)

### Behavior

- Validate that the organization exists (Exit 2 if not found)
- Validate that each `user_id` refers to a valid `User` object (registered or unregistered)
- Validate that each user is **not already a member** of the organization (Exit 3 conflict if already present)
- If a role is provided, validate that it exists within the organization (Exit 4 if role not found)
- Add each user as a new `OrganizationMembership`
- Assign role if provided

### Success Criteria

- Valid users are added as members of the organization
- Partial success: valid users are added; invalid users are skipped with errors printed
- If no users are provided → Exit code 5 with message "No users provided."

### Error Handling

- Exit 1 → Missing required arguments (org ID or user ID)
- Exit 2 → Organization not found
- Exit 3 → User already a member of org
- Exit 4 → Role not found
- Exit 5 → No users provided

---

## Test Cases

- ✅ Add one valid user with a valid role
- ✅ Add multiple users in one call, some already in org, some not
- ✅ Add with no role → default/null role
- ❌ Add to non-existent organization → Exit 2
- ❌ Add with unknown user ID → skip user, log error
- ❌ Add with invalid role → Exit 4
- ❌ Call with no users → Exit 5

---

## Non-goals / Future Ideas

- Support adding users by email or name
- Bulk imports from external sources

---

## Examples Required

- CLI adding one user with role
- CLI adding multiple users without role
- CLI output showing partial success

---

## Docs Required

- CLI doc for `add-org-user`
- Updated OrganizationMembership model doc
- Role resolution logic and examples

---

## Edge Cases

- Duplicate `--user-id` in the same call → de-dupe silently
- Users with no email (unregistered) → still allowed
- Role case-insensitive match (e.g., "Manager" == "manager")

---

## Required Models

- `OrganizationMembership(user_id, organization_id, role_id)`
- `Role(id, name, organization_id)`
