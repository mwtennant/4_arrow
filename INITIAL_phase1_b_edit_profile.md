# Requirements

## get-profile command

- Syntax (exactly **one** id flag required):  
  `python main.py get-profile --user-id 123`  
  `python main.py get-profile --email alice@example.com`  
  `python main.py get-profile --usbc-id 555555`  
  `python main.py get-profile --tnba-id 98765`
- Output: **Rich table** with columns  
  `user_id · first · last · email · phone · address · usbc_id · tnba_id`
- If user not found → print “No user found.” and exit code **1**.

## edit-profile command

- Syntax:  
  `python main.py edit-profile --user-id <id> [--first FIRST] [--last LAST] [--phone PHONE] [--address ADDRESS]`
- At least one field must be supplied; email is immutable.
- Validation: empty strings not allowed.

## delete-profile command

- Syntax:  
  `python main.py delete-profile --user-id <id> --confirm yes`
- Must refuse if `--confirm yes` not supplied or id does not exist.

### Shared

- Use SQLAlchemy session in `core/profile.py`.
- Friendly errors → exit code 1.
- Coverage ≥ 85 %.

### Tests

- get-profile by user-id ⇒ returns correct row
- get-profile by email ⇒ returns correct row
- get-profile with two id flags ⇒ exit 1
- get-profile non-existent ⇒ “No user found”, exit 1
- edit-profile success ⇒ fields updated
- edit-profile invalid user ⇒ exit 1
- delete-profile success ⇒ row deleted, exit 0
- delete-profile without confirm ⇒ exit 1

### Non-goal line

- Editing by email reserved for future slice
