# Global Rules for Claude Code

You are an AI pair-programmer. Follow these conventions unless overridden by a feature prompt.

## Coding conventions

- Python 3.12, PEP 8 compliant
- Type hints required
- Google-style docstrings
- snake_case for vars/functions, PascalCase for classes

## Architecture

- CLI entry points in `main.py` unless the PRP says otherwise
- Separate `core/` and `storage/` layers for persistence

## Testing

- pytest, coverage ≥ 85 %

## Output

- Emit code only inside fenced blocks
- Commit messages follow Conventional Commits
