# Quickstart: Auto-Export Environment Variables

**Feature**: 002-auto-export-env  
**Date**: 2026-03-13

## Setup

```bash
git checkout 002-auto-export-env
uv sync --dev
```

## Test the feature

### Interactive login with auto-export (PowerShell)

```powershell
dotaws login --profile <your-profile> | Invoke-Expression
# Or simply:
dotaws login --profile <your-profile>
# Then answer "Y" to the export prompt
```

### Interactive login with auto-export (Bash/Zsh)

```bash
eval "$(dotaws login --profile <your-profile>)"
# Or simply:
dotaws login --profile <your-profile>
# Then answer "Y" to the export prompt
```

### Verify export worked

```bash
echo $AWS_PROFILE
# Should print your profile name
```

### Decline export (fallback to print)

```bash
dotaws login --profile <your-profile>
# Answer "n" to the export prompt
# Export statements are printed for manual copy-paste
```

### Non-interactive (unchanged)

```bash
dotaws login --profile <your-profile> --non-interactive
# Prints export statements directly, no prompt
```

## Run tests

```bash
uv run pytest tests/ -q
uv run ruff check .
uv run mypy src/
```

## Quality gates

All must pass:
- `uv run pytest` — all tests green
- `uv run ruff check .` — no lint errors
- `uv run mypy src/` — no type errors
