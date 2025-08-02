# Feature: Add Organization Data Models (phase-org-c)

## One-Sentence Purpose

Introduce core database models to support organization membership, roles, permissions, and their relationships.

---

## Requirements

### New Models (in `core/models.py`)

#### 1. `Permission`

```python
id: int (PK)
name: str (unique per organization, case-insensitive)
description: Optional[str]
organization_id: FK to Organization
```

- Constraint: Unique (lower(name), organization_id)
- Optional max lengths: name ≤ 64, description ≤ 255

#### 2. `Role`

```python
id: int (PK)
name: str (unique per organization, case-insensitive)
organization_id: FK to Organization
```

- Constraint: Unique (lower(name), organization_id)
- Future-proofing: allow for hierarchy with optional `parent_role_id`

#### 3. `RolePermission`

```python
id: int (PK)
role_id: FK to Role
permission_id: FK to Permission
```

- Constraint: Unique (role_id, permission_id)
- Notes: Enables many-to-many mapping of roles to permissions

#### 4. `OrganizationMembership`

```python
id: int (PK)
user_id: FK to User
organization_id: FK to Organization
role_id: Optional[FK to Role]
is_registered: bool
```

- Constraint: Unique (user_id, organization_id)
- `is_registered` determined by whether user has a password/login or verified email

---

## Migration Support

- Create SQLAlchemy migration script for the four new tables
- Apply necessary indices and constraints as above
- Update database initialization logic in `storage/database.py`

---

## Success Criteria

- Models are available for import in `core/models.py`
- All relationships and constraints compile successfully
- Database migration runs cleanly with Alembic (if used)

---

## Test Coverage

- Unit tests for:

  - Unique constraints
  - FK constraints
  - Role → Permission resolution
  - Membership creation with and without roles

- Coverage target: ≥ 90% for these models

---

## Non-goals / Future Ideas

- No soft deletes or archival support
- No multi-org ownership per user (yet)
- No org invitations/invitability rules yet

---

## Examples Required

- Sample Role with 2 permissions
- Sample Membership with a role

---

## Docs Required

- `core/models.py` annotations for each new model
- Relationship map in markdown or mermaid format

---

## Edge Cases

- Duplicate names differing only by case → rejected
- Membership creation with invalid role ID → FK error
- Role assigned to non-existent permission → fails FK
- Permissions reused across roles → allowed

---

## Order Dependencies

- Must be implemented before any other org feature that uses roles, permissions, or membership
