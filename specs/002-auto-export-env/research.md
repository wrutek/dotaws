# Research: Auto-Export Environment Variables

**Feature**: 002-auto-export-env  
**Date**: 2026-03-13

## Research Summary

No unknowns required investigation. This feature modifies an existing flow with well-understood constraints.

## Decision: Export Mechanism

- **Decision**: Output eval-ready shell script to stdout; the shell hook or user wraps it with `eval` / `Invoke-Expression`.
- **Rationale**: A child process (Python CLI) cannot set environment variables in its parent shell. This is a fundamental OS constraint. The existing hook flow already uses this pattern successfully. The login command will use the same approach.
- **Alternatives considered**:
  - Direct `os.environ` mutation: Only affects the Python process, not the parent shell. Rejected.
  - Temp file + source: Adds file I/O, cleanup burden, and security risk (credentials on disk). Rejected.
  - Named pipe / IPC: Over-engineered for this use case. Rejected.

## Decision: Confirmation Prompt Placement

- **Decision**: Add the confirm/decline branch inside the existing `login()` typer command function, after `execute_login()` returns the script string.
- **Rationale**: `execute_login()` is also called by `hook_check()` which already handles its own export flow. Changing `execute_login()` would break the hook path. The prompt belongs in the CLI layer only.
- **Alternatives considered**:
  - Modify `execute_login()` to return a richer object: Would require changes to hook_check() caller. Unnecessary coupling. Rejected.

## Decision: TTY Detection

- **Decision**: Use `sys.stdout.isatty()` to detect piped/redirected output.
- **Rationale**: Standard Python mechanism, no dependencies, works on all platforms.
- **Alternatives considered**: None — this is the canonical approach.

## Decision: Overwrite Warning

- **Decision**: Check `os.environ` for existing AWS_* keys before export; print a warning listing which will be overwritten; proceed without second confirmation.
- **Rationale**: User already confirmed export. A second confirmation for overwrite would be annoying for the most common workflow (re-login / profile switch).
- **Alternatives considered**: Silent overwrite (user chose "warn then overwrite" in clarification).
