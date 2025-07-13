# Step (PRP)

- **Steps** information

  - 1-A Signup + Login Depends on: Nothing
    - Proves account creation, hashing, DB connectivity, CLI plumbing.
  - 1-B Edit Profile Depends on: 1-A
    - Adds update flow (update_profile) and CLI command; exercises read/write, validation, tests optional fields.
  - 1-C Add other non member contacts Depends on: 1-A
    - Demonstrates a relationship table (contacts) and simple query.
  - 1-D Merge Profiles Depends on: 1-B, 1-C
    - More complex update that touches users + contacts; needs conflict resolution UI.
  - 1-E Authentication hardening (optional) Depends on: 1-A
    - Add JWT tokens or session management if you need an API later

- deliver each slice to main before starting the next. That way regressions are caught early and context is fresh for the next PRP

## Context Engineering Steps for each slice

1. Add that INITIAL file.
2. claude /generate-prp {phase name}.md
3. Review the PRP
4. /execute-prp PRPs/ {phase name}.md
5. Manually run new commands to verify.
6. Merge branch → Phase 1 done.

## How a phase wraps up

1. All slices merged; full Phase 1 test suite still green.
2. Run an end-to-end smoke demo: signup → edit profile → add contact → merge profiles.
3. Update docs/ROADMAP.md marking Phase 1 ✅.
4. Hold a mini-retro: add lessons to DECISIONS.md, prune examples/docs.
5. Tag a release (v0.1.0) before moving to Phase 2 (e.g., inventory import).

⸻
