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
- `1` - Error (user not found, validation error, etc.)
- `2` - CLI validation error (missing required options)

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

### Create and Manage a User

```bash
# 1. Create user
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
