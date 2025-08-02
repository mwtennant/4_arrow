# Role Terminology Migration Guide

This guide helps you migrate from the legacy `member/non-member` terminology to the new role-based system.

## Overview

The 4th Arrow Tournament Control application has migrated from binary member classification to explicit role-based user classification:

| Old Term | New Role | Description |
|----------|----------|-------------|
| Member | Registered User | Users who created their own account (have email/password) |
| Non-member | Unregistered User | Users added by operators but who have not signed up yet |
| *(new)* | Organization Member | Registered users who belong to the tournament organization |

## For Developers

### Code Migration

**Old Code:**
```python
# Legacy property (deprecated)
if user.is_member:
    send_email_notification(user)
```

**New Code:**
```python
# New role helper methods
if user.is_registered_user():
    send_email_notification(user)

# Or check specific role
if user.get_role() == ProfileRole.REGISTERED_USER:
    send_email_notification(user)
```

### Role Helper Methods

The `User` model now provides three boolean accessor methods:

```python
user.is_registered_user()    # Has email, can authenticate
user.is_unregistered_user()  # No email, tournament-only profile  
user.is_org_member()         # Organization member with privileges
```

### Role Enum Values

```python
from core.models import ProfileRole

ProfileRole.REGISTERED_USER    # "registered_user"
ProfileRole.UNREGISTERED_USER  # "unregistered_user" 
ProfileRole.ORG_MEMBER         # "org_member"
```

## For CLI Users

### Command Changes

**Old Command:**
```bash
# Legacy flag (still works with deprecation warning)
./run list-users --member
```

**New Command:**
```bash
# New role-based filtering
./run list-users --role registered_user
./run list-users --role unregistered_user
./run list-users --role org_member
```

### All Available Role Values

- `registered_user` - Users with email who can log in
- `unregistered_user` - Users without email (tournament-only)
- `org_member` - Organization staff/admin users

## For API/JSON Users

### JSON Field Migration

**Legacy JSON Export:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "is_member": true
}
```

**New JSON Format:**
```json
{
  "id": 1,
  "name": "John Doe", 
  "email": "john@example.com",
  "role": "registered_user"
}
```

### Compatibility Layer

During the migration period, a compatibility shim is available:

```python
from utils.legacy_shim import export_users_to_json_with_legacy

# Export with legacy is_member field for backward compatibility
legacy_json = export_users_to_json_with_legacy(users_data)
```

## Database Migration

### Running the Migration

1. **Check Current Status:**
   ```bash
   python scripts/migrate_role_terminology.py --status
   ```

2. **Dry Run (Recommended First):**
   ```bash
   python scripts/migrate_role_terminology.py --dry-run
   ```

3. **Execute Migration:**
   ```bash
   python scripts/migrate_role_terminology.py
   ```

### Migration Process

The migration script will:
1. Add `role VARCHAR(32)` column to users table
2. Backfill role data based on existing user profiles
3. Create performance index for role-based queries
4. Verify migration integrity

### Role Assignment Logic

The migration determines roles based on existing user data:

- **Registered User**: Has email address (not org domain)
- **Unregistered User**: No email address or empty email
- **Organization Member**: Email ends with `@tournamentorg.com` or `@admin.com`

## Migration Timeline

### Phase User: Implementation (Completed)
- ✅ Core role system implementation
- ✅ CLI flag migration with backward compatibility
- ✅ Database migration script
- ✅ JSON compatibility layer
- ✅ Comprehensive testing and documentation

### Phase 2: Cleanup (Scheduled: +90 days)
- 🔄 Remove deprecated `is_member` property
- 🔄 Remove legacy CLI flag support
- 🔄 Remove JSON compatibility shim
- 🔄 Update external integration docs

## Deprecation Warnings

During the migration period, you may see warnings like:

```
DeprecationWarning: is_member is deprecated. Use is_registered_user() instead.
```

```
DeprecationWarning: --member flag is deprecated. Use --role registered_user instead.
```

These warnings help identify code that needs updating. Update your code to use the new role methods and CLI flags.

## FAQ

### Q: Will my existing data be preserved?
**A:** Yes, the migration preserves all existing user data and determines appropriate roles based on current user profiles.

### Q: Do I need to update external integrations immediately?
**A:** No, the JSON compatibility layer maintains backward compatibility during the migration period. However, you should plan to update to the new role field within 90 days.

### Q: What if the migration fails?
**A:** The migration script includes verification and rollback capabilities. Run with `--dry-run` first to preview changes.

### Q: Can I still use the old `is_member` property?
**A:** Yes, but it's deprecated and will issue warnings. It currently maps to `is_registered_user()` for compatibility.

### Q: How do I identify organization members?
**A:** Organization members are users with email addresses ending in configured org domains (`@tournamentorg.com`, `@admin.com`) or users explicitly assigned the `org_member` role.

## Need Help?

- Review [ADR-008](./ADR-008-role-terminology.md) for technical decision details
- Check test files for usage examples
- Run migration script with `--help` for command options
- Contact the development team for integration assistance