# 4th Arrow Tournament Control - CLI Reference

This document provides a complete reference for all CLI commands in the 4th Arrow Tournament Control application.

## Getting Started

Always activate the virtual environment before running commands:

```bash
source venv/bin/activate
```

**Note about long commands:** For longer commands, you can either:

1. Type the entire command on one line
2. Use backslashes (`\`) to split the command across multiple lines for readability

If you copy-paste commands that span multiple lines without backslashes, the terminal may interpret each line as a separate command.

## User Authentication Commands

### signup

Create a new user account.

**Syntax:**

```bash
python main.py signup --email <email> --password <password> --first <first_name> --last <last_name> --phone <phone> [--address <address>] [--usbc_id <usbc_id>] [--tnba_id <tnba_id>]
```

**Multi-line format (for readability):**

```bash
python main.py signup \
  --email <email> \
  --password <password> \
  --first <first_name> \
  --last <last_name> \
  --phone <phone> \
  [--address <address>] \
  [--usbc_id <usbc_id>] \
  [--tnba_id <tnba_id>]
```

**Required Options:**

- `--email` - User email address (must be unique)
- `--password` - User password
- `--first` - User first name
- `--last` - User last name
- `--phone` - User phone number

**Optional Options:**

- `--address` - User address
- `--usbc_id` - User USBC ID
- `--tnba_id` - User TNBA ID

**Examples:**

```bash
# Minimal signup
python main.py signup --email john@example.com --password secret123 --first John --last Doe --phone 555-1234

# Signup with all fields
python main.py signup --email alice@example.com --password secure456 --first Alice --last Smith --phone 555-5678 --address "123 Main St" --usbc_id 123456 --tnba_id 789012

# Signup with all fields (multi-line format)
python main.py signup \
  --email alice@example.com \
  --password secure456 \
  --first Alice \
  --last Smith \
  --phone 555-5678 \
  --address "123 Main St" \
  --usbc_id 123456 \
  --tnba_id 789012
```

**Success Output:**

```
User account created successfully for john@example.com
```

**Error Cases:**

- Duplicate email: `Error: Email already exists`
- Invalid email format: `Error: Invalid email format`
- Missing required fields: `Missing option --first`

---

### login

Authenticate with existing credentials.

**Syntax:**

```bash
python main.py login --email <email> --password <password>
```

**Required Options:**

- `--email` - User email address
- `--password` - User password

**Examples:**

```bash
python main.py login --email john@example.com --password secret123
```

**Success Output:**

```
Login successful. Welcome, John Doe!
```

**Error Cases:**

- Invalid credentials: `Error: Invalid email or password`
- Missing credentials: `Missing option --password`

---

## User Creation Commands

### create

Create a new user in the system. Users can be created as non-members (without email) or members (with email).

**Syntax:**

```bash
python main.py create --first <first_name> --last <last_name> [--address <address>] [--usbc_id <usbc_id>] [--tnba_id <tnba_id>] [--phone <phone>] [--email <email>]
```

**Multi-line format (for readability):**

```bash
python main.py create \
  --first <first_name> \
  --last <last_name> \
  [--address <address>] \
  [--usbc_id <usbc_id>] \
  [--tnba_id <tnba_id>] \
  [--phone <phone>] \
  [--email <email>]
```

**Required Options:**

- `--first` - First name (cannot be empty)
- `--last` - Last name (cannot be empty)

**Optional Options:**

- `--address` - User address
- `--usbc_id` - USBC ID (must be unique if provided)
- `--tnba_id` - TNBA ID (must be unique if provided)
- `--phone` - Phone number
- `--email` - Email address (must be unique if provided)

**Examples:**

```bash
# Create non-member bowler (minimum required fields)
python main.py create --first Bob --last Lane

# Create member with email
python main.py create --first Alice --last Smith --email alice@example.com

# Create user with all fields
python main.py create --first John --last Doe --email john@example.com --phone 555-1234 --address "123 Main St" --usbc_id 12345 --tnba_id 67890

# Create user with all fields (multi-line format)
python main.py create \
  --first John \
  --last Doe \
  --email john@example.com \
  --phone 555-1234 \
  --address "123 Main St" \
  --usbc_id 12345 \
  --tnba_id 67890
```

**Success Output:**

```
# Without email
User created successfully: Bob Lane

# With email
User created successfully: Alice Smith (alice@example.com)
```

**Error Cases:**

- Empty first name: `ERROR: First name cannot be empty` (Exit code: 3)
- Empty last name: `ERROR: Last name cannot be empty` (Exit code: 3)
- Duplicate email: `ERROR: Email already exists. Try using get-profile to find the existing user.` (Exit code: 2)
- Duplicate USBC ID: `ERROR: USBC ID already exists in the database.` (Exit code: 2)
- Duplicate TNBA ID: `ERROR: TNBA ID already exists in the database.` (Exit code: 2)
- Database error: `ERROR: Database error occurred: <details>` (Exit code: 1)

---

## Profile Management Commands

### get-profile

Retrieve user profile information. **Exactly one ID flag must be provided.**

**Syntax:**

```bash
python main.py get-profile --user-id <id>
python main.py get-profile --email <email>
python main.py get-profile --usbc_id <usbc_id>
python main.py get-profile --tnba_id <tnba_id>
```

**ID Options (choose exactly one):**

- `--user-id` - User ID number
- `--email` - Email address
- `--usbc_id` - USBC ID
- `--tnba_id` - TNBA ID

**Examples:**

```bash
# Get by user ID
python main.py get-profile --user-id 123

# Get by email
python main.py get-profile --email alice@example.com

# Get by USBC ID
python main.py get-profile --usbc_id 555555

# Get by TNBA ID
python main.py get-profile --tnba_id 98765
```

**Success Output:**
Rich table with columns: `user_id · first · last · email · phone · address · usbc_id · tnba_id`

**Error Cases:**

- No user found: `ERROR: No user found.`
- Multiple ID flags: `ERROR: Exactly one ID flag must be provided`
- No ID flags: `ERROR: Exactly one ID flag must be provided`

---

### edit-profile

Edit user profile fields. **At least one field must be provided. Email is immutable.**

**Syntax:**

```bash
python main.py edit-profile --user-id <id> [--first <first_name>] [--last <last_name>] [--phone <phone>] [--address <address>]
```

**Required Options:**

- `--user-id` - User ID to edit

**Optional Field Options (at least one required):**

- `--first` - New first name
- `--last` - New last name
- `--phone` - New phone number
- `--address` - New address

**Examples:**

```bash
# Edit single field
python main.py edit-profile --user-id 123 --first "John Michael"

# Edit multiple fields
python main.py edit-profile --user-id 123 --first Alice --phone 555-1234

# Update address
python main.py edit-profile --user-id 123 --address "456 Oak Street"
```

**Success Output:**

```
Profile updated.
```

**Error Cases:**

- User not found: `ERROR: User not found`
- No fields provided: `ERROR: At least one field must be provided`
- Empty string: `ERROR: First name cannot be empty`

---

### delete-profile

Delete a user profile. **Confirmation required.**

**Syntax:**

```bash
python main.py delete-profile --user-id <id> --confirm yes
```

**Required Options:**

- `--user-id` - User ID to delete
- `--confirm` - Must be exactly "yes"

**Examples:**

```bash
# Delete profile with confirmation
python main.py delete-profile --user-id 123 --confirm yes
```

**Success Output:**

```
Profile deleted.
```

**Error Cases:**

- User not found: `ERROR: User not found`
- Missing confirmation: `ERROR: Deletion aborted.`
- Wrong confirmation: `ERROR: Deletion aborted.`

---

### list-users

List all users in the system with optional filtering capabilities. This command supports flexible search by allowing operators to apply zero or multiple filters to narrow down results.

**Syntax:**

```bash
python main.py list-users [--first <first_name>] [--last <last_name>] [--email <email>] [--phone <phone>] [--address <address>] [--usbc_id <usbc_id>] [--tnba_id <tnba_id>]
```

**All Options are Optional (Filters):**

- `--first` - Filter by first name (partial match, case-insensitive)
- `--last` - Filter by last name (partial match, case-insensitive)
- `--email` - Filter by email address (partial match, case-insensitive)
- `--phone` - Filter by phone number (partial match, case-insensitive)
- `--address` - Filter by address (partial match, case-insensitive)
- `--usbc_id` - Filter by USBC ID (exact match)
- `--tnba_id` - Filter by TNBA ID (exact match)

**Filter Behavior:**

- **Partial matching:** String fields (first, last, email, phone, address) support partial, case-insensitive matching
- **Exact matching:** ID fields (usbc_id, tnba_id) require exact matches
- **Multiple filters:** All filters are combined with logical AND operations (not OR)
- **Empty filters:** Empty strings or whitespace-only filters are ignored

**Examples:**

```bash
# List all users in the system
python main.py list-users

# Find users by first name
python main.py list-users --first John

# Find users by last name
python main.py list-users --last Smith

# Find users by email domain
python main.py list-users --email @gmail.com

# Find users by phone area code
python main.py list-users --phone 555

# Find users by address
python main.py list-users --address "Main St"

# Find users by exact USBC ID
python main.py list-users --usbc_id 12345

# Find users by exact TNBA ID
python main.py list-users --tnba_id 67890

# Combine multiple filters (AND logic)
python main.py list-users --first John --email john@example.com

# Complex multi-field search
python main.py list-users --first Alice --address "Main St" --phone 555
```

**Sample Output:**

```
┏━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃ User ID ┃ First ┃ Last  ┃ Email                  ┃ Phone        ┃ Address                ┃ USBC ID ┃ TNBA ID ┃
┡━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ 1       │ John  │ Doe   │ john@example.com       │ 555-1234     │ 123 Main St            │ 12345   │ 67890   │
│ 2       │ Jane  │ Smith │ jane@example.com       │ 555-5678     │ 456 Oak Ave            │ 54321   │ 09876   │
│ 3       │ Bob   │ Lane  │                        │              │                        │         │         │
└─────────┴───────┴───────┴────────────────────────┴──────────────┴────────────────────────┴─────────┴─────────┘
```

**Empty Results:**

When no users match the filter criteria:

```
No users found matching criteria.
```

**Error Cases:**

- Database connection failure: `ERROR: Database error occurred: <details>` (Exit code: 1)
- Unexpected error: `ERROR: An unexpected error occurred: <details>` (Exit code: 1)

**Use Cases:**

- **Find all users:** Run without any filters to see complete user list
- **Search by name:** Use `--first` and/or `--last` to find users by name
- **Contact lookup:** Use `--email` or `--phone` to find users by contact info
- **ID verification:** Use `--usbc_id` or `--tnba_id` for exact ID matches
- **Address search:** Use `--address` to find users in specific locations
- **Complex filtering:** Combine multiple filters to narrow down results

---

### merge

Merge one or more user profiles into a main profile. This resolves duplicate or overlapping user records by combining data and handling conflicts through interactive prompts.

**Syntax:**

```bash
python main.py merge --main-id <main_user_id> --merge-id <merge_user_id> [--merge-id <additional_merge_user_id>]...
```

**Required Options:**

- `--main-id` - ID of the primary user to merge into (integer)
- `--merge-id` - ID(s) of user(s) to merge (integer, can be repeated for multiple merges)

**Examples:**

```bash
# Merge a single user into another
python main.py merge --main-id 3 --merge-id 5

# Merge multiple users into a main profile
python main.py merge --main-id 3 --merge-id 5 --merge-id 11

# Example with more users
python main.py merge --main-id 1 --merge-id 2 --merge-id 3 --merge-id 4
```

**Interactive Conflict Resolution:**

When conflicting field values are detected (different non-empty values for email, phone, address, usbc_id, or tnba_id), the system will prompt for resolution:

```
Conflicting phone numbers found:
Main user (ID 3): 555-1234
Merge user (ID 5): 555-5678
Choose which value to keep [1=main, 2=merge, s=skip]: 1

Conflicting addresses found:
Main user (ID 3): 123 Main St
Merge user (ID 5): 456 Oak Ave
Choose which value to keep [1=main, 2=merge, s=skip]: 2

Summary of changes:
- Phone: Keeping main user value (555-1234)
- Address: Using merge user value (456 Oak Ave)

Proceed with merge? [y/N]: y
```

**Conflict Resolution Options:**

- `1` - Keep the main user's value
- `2` - Keep the merge user's value
- `s` - Skip this field (keep main user's value unchanged)

**Final Confirmation:**
After resolving all conflicts, the system shows a summary and asks for final confirmation before completing the merge.

**Success Output:**

```
Profile merge completed successfully.
```

**Merge Behavior:**

- Non-conflicting fields: Merge user data fills empty fields in main user
- Conflicting fields: Interactive resolution required
- Post-merge: Merged users are deleted, all data consolidated in main user
- Transaction safety: All operations wrapped in database transaction

**Error Cases:**

- Invalid main user ID: `ERROR: Main user with ID <id> not found` (Exit code: 4)
- Invalid merge user ID: `ERROR: Merge user with ID <id> not found` (Exit code: 4)
- Self-merge attempt: `ERROR: Cannot merge user <id> into themselves` (Exit code: 4)
- Missing main ID: `ERROR: --main-id is required` (Exit code: 4)
- Missing merge IDs: `ERROR: At least one --merge-id is required` (Exit code: 4)
- Database error: `ERROR: Database error occurred: <details>` (Exit code: 1)

**User Cancellation:**

- Users can cancel the operation at any time by responding `n` to the final confirmation
- Users can press Ctrl+C to abort during interactive prompts

---

## General Commands

### help

Display help information.

**Syntax:**

```bash
python main.py --help
python main.py <command> --help
```

**Examples:**

```bash
# General help
python main.py --help

# Command-specific help
python main.py signup --help
python main.py get-profile --help
```

---

## Exit Codes

- `0` - Success
- `1` - Error (user not found, validation error, database error, etc.)
- `2` - Duplicate constraint violation (email, USBC ID, TNBA ID already exists)
- `3` - Empty required field validation error (first/last name cannot be empty)
- `4` - Invalid user ID or merge validation error (user not found, self-merge attempt)

---

## Notes

- All error messages are prefixed with "ERROR:" for consistency
- Email addresses must be unique across all users
- Empty strings are not allowed for any field updates
- The email field cannot be modified after account creation
- Rich table output uses minimal borders for profile display
- All commands require the virtual environment to be activated

---

## Common Workflows

### Create Users (Non-Members and Members)

```bash
# 1. Create non-member bowler (minimum fields)
python main.py create --first Bob --last Lane

# 2. Create member with email
python main.py create --first Alice --last Smith --email alice@example.com

# 3. Create full user with all details
python main.py create --first John --last Doe --email john@example.com --phone 555-1234 --address "123 Main St" --usbc_id 12345 --tnba_id 67890

# 4. View created user
python main.py get-profile --user-id 1
```

### Create and Manage a User Account (Full Authentication)

```bash
# 1. Create user account with authentication
python main.py signup --email user@example.com --password pass123 --first John --last Doe --phone 555-1234

# 2. View profile
python main.py get-profile --email user@example.com

# 3. Update profile
python main.py edit-profile --user-id 1 --address "123 New Street"

# 4. View updated profile
python main.py get-profile --user-id 1

# 5. Delete profile (if needed)
python main.py delete-profile --user-id 1 --confirm yes
```

### Profile Lookup Options

```bash
# Find user by different identifiers
python main.py get-profile --user-id 1
python main.py get-profile --email user@example.com
python main.py get-profile --usbc_id 123456
python main.py get-profile --tnba_id 789012
```

### User Search and Listing

```bash
# List all users in the system
python main.py list-users

# Find users by name
python main.py list-users --first John
python main.py list-users --last Smith

# Find users by contact information
python main.py list-users --email john@example.com
python main.py list-users --phone 555-1234

# Find users by IDs
python main.py list-users --usbc_id 12345
python main.py list-users --tnba_id 67890

# Complex searches with multiple filters
python main.py list-users --first John --last Doe
python main.py list-users --phone 555 --address "Main St"
python main.py list-users --first Alice --email alice@example.com --phone 555

# Search by partial matches
python main.py list-users --email @gmail.com
python main.py list-users --address "Main St"
python main.py list-users --phone 555
```

### Merge Duplicate Profiles

```bash
# 1. Find potential duplicate users
python main.py get-profile --email john@example.com
python main.py get-profile --email john.doe@example.com

# 2. Merge the duplicate into the main profile
python main.py merge --main-id 3 --merge-id 5

# 3. Verify the merge was successful
python main.py get-profile --user-id 3

# 4. Multiple user merge example
python main.py merge --main-id 1 --merge-id 2 --merge-id 3
```
