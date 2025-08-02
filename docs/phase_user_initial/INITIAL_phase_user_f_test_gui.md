# FEATURE: GUI – Minimal Visual Test Interface (Phase User-F)

## Summary

Design and implement a minimal, visually clean GUI to support operator testing workflows.  
This will serve as the foundation for both developer and production GUIs going forward.

## Goals

- Provide a fast and clear visual interface for testing users, tournaments, and other entities.
- Establish layout and component architecture for future production use.
- Stay lightweight: minimal CSS, clean design, and no JavaScript frameworks (if avoidable).

## Requirements

### Functional Pages

- ✅ **Login / Create Account page**
- ✅ **Landing Page**
  - Greeting: "Hello {user name}, what are you testing now?"
- ✅ **Navigation Bar (Top)**
  - Users
  - Organizations
  - Tournaments
  - Settings
- ✅ **Sidebar (Contextual Navigation)**
  - For each top-level tab (e.g., Users → Add User, Delete User, List Users)

### Design Guidelines

- Minimalist layout
- Clean type hierarchy (headings, labels, fields)
- Use system fonts or simple web-safe fonts (e.g., `sans-serif`, `inter`)
- Limit CSS to layout, spacing, and readability (not stylistic embellishments)
- Avoid heavy animations or visual noise

### Data & Backend

- Use SQLAlchemy ORM to read/write to `inventory.db`
- Reuse models from `core/models.py`
- Establish clear routes for each section (can use Flask or FastAPI with templates)
- Keep server logic minimal; frontend is mostly read and navigate

### File Locations

- GUI App: `src/gui/`
- Templates: `src/gui/templates/`
- Static assets (CSS): `src/gui/static/`
- Tests: `tests/gui/`

## Tests Required

- ✅ Page loads for all main routes
- ✅ Sidebar renders correct functions per section
- ✅ Database-backed list renders (e.g. Users list)
- ✅ Login / Create workflows validate input
- ✅ Edge cases: No users, broken DB connection

## Code Coverage

- Target ≥ 85% for all backend and route logic
- Frontend template tests optional unless templating includes logic

## Non-Goals / Future Work

- No full user profile editing forms
- No scoring interface
- No dark/light theme toggle
- No client-side JS logic beyond default browser behaviors
- No mobile/tablet responsiveness in Phase User

## Example Usage

1. Operator visits `/login`
2. Logs in → lands on personalized home screen
3. Clicks “Users” → sees sidebar options: Add User, List Users
4. Clicks “List Users” → sees live table of users from DB

## Docs Required

- https://flask.palletsprojects.com/ (or FastAPI)
- https://jinja.palletsprojects.com/
- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- CLAUDE.md for formatting, typing, and test coverage rules

## Edge Cases

- No users in database → graceful “No users found” message
- Sidebar context doesn't match tab → defaults to safe fallback
- Database unavailable → show global error state
- Invalid login → form validation + retry option
- User has no name → fallback to "Hello, tester"

## Notes

This is the testbed for the real GUI. Favor readability and functionality over polish. Think “developer tool,” not “production UI.” The frontend can use Jinja templating with server-side rendering to keep things simple.
