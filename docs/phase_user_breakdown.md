# Step (PRP)

- **Steps** information

  - User-A Signup + Login Depends on: Nothing
    - Proves account creation, hashing, DB connectivity, CLI plumbing.
  - User-B Edit Profile Depends on: User-A
    - Adds update flow (update_profile) and CLI command; exercises read/write, validation, tests optional fields.
  - User-C Add other non member contacts Depends on: User-A
    - Demonstrates a relationship table (contacts) and simple query.
  - User-D Merge Profiles Depends on: User-B, User-C
    - More complex update that touches users + contacts; needs conflict resolution UI.
  - User-E Authentication hardening (optional) Depends on: User-A
    - Add JWT tokens or session management if you need an API later

- deliver each slice to main before starting the next. That way regressions are caught early and context is fresh for the next PRP

## Context Engineering Steps for each slice

1. Add that INITIAL file.
2. claude /generate-prp {phase name}.md
3. Review the PRP
4. /execute-prp PRPs/ {phase name}.md
5. Manually run new commands to verify.
6. Merge branch → Phase User done.

## How a phase wraps up

1. All slices merged; full Phase User test suite still green.
2. Run an end-to-end smoke demo: signup → edit profile → add contact → merge profiles.
3. Update docs/ROADMAP.md marking Phase User ✅.
4. Hold a mini-retro: add lessons to DECISIONS.md, prune examples/docs.
5. Tag a release (v0.1.0) before moving to Phase 2 (e.g., inventory import).

⸻
