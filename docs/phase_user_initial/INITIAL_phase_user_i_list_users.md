# Product Requirements Prompt: List Users Enhancements (Phase 1‑E)

## Summary

Extend the `list-users` command with robust filtering, ordering, and CSV export so operators can generate ad‑hoc reports quickly.

## Requirements

```
list-users [--role <registered|unregistered|org_member>]
           [--created-since YYYY-MM-DD]
           [--order <id|last_name|created_at>]
           [--csv <output_path>]
           [--page-size N]
```

- **Default output**: Rich table with zebra striping; columns `id`, `name`, `role`, `email`, `created_at`.
- **Paging**: if result > page‑size show “Next \[N] remaining…” prompt.
- **CSV export** writes the same columns, RFC 4180‑compliant.
- Function returns `List[Dict]` so GUI/API layers can reuse the data.
- **Unit tests**: filter combinations, paging logic, CSV round‑trip with Unicode names.
- Gracefully handle DB errors, exit code 4.

## Non‑Goals

- GUI address book (Phase 2‑C).
- Sorting on arbitrary columns beyond the three specified.

## Docs Required

- Update CLI help and README report examples.

## Edge‑Cases

- Filtering by date across a DST change.
- Unicode characters in last names rendered in both Rich and CSV outputs.
