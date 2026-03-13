# Data Model: Auto-Export Environment Variables

**Feature**: 002-auto-export-env  
**Date**: 2026-03-13

## Entity Changes

**No new entities.** This feature modifies behavior in the existing `login()` command function only.

### Existing Entities (unchanged)

| Entity | Change | Notes |
|--------|--------|-------|
| `ShellExportPayload` | None | Already contains `script` (eval-ready string) and `env` (dict) |
| `InvocationMode` | None | Already has `INTERACTIVE` / `NON_INTERACTIVE` |
| `AuthenticatedSession` | None | Already has `env_map` property |

### New Functions (in existing modules)

| Module | Function | Purpose |
|--------|----------|---------|
| `dotaws.shared.io` | `print_warning(message: str) -> None` | Print a yellow warning message via Rich console |
| `dotaws.cli.commands.login` | `_check_existing_env_vars(env: dict[str, str]) -> list[str]` | Return list of AWS env var names that already exist in `os.environ` |
