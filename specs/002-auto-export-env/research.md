# Research: Auto-Export Environment Variables

**Feature**: 002-auto-export-env  
**Date**: 2026-03-13

## Research Summary

Core challenge: a child process cannot modify its parent shell's environment. Investigated mechanisms used by established CLI tools (`conda`, `nvm`, `direnv`, `pyenv`) and selected a shell wrapper function approach.

## Decision: Export Mechanism — Shell Wrapper Function

- **Decision**: Provide a shell wrapper function that intercepts `dotaws login`, calls the real binary, and applies the exported env vars directly in the current shell session.
- **Rationale**: A child process (Python CLI) cannot set environment variables in its parent shell — this is a fundamental OS constraint. However, a **shell function** runs in the shell's own process and *can* modify its environment. This is the same proven pattern used by:
  - `conda activate` — shell function wraps conda binary
  - `nvm use` — shell function applies env changes
  - `direnv hook` — eval-based hook sets vars on cd
  - The existing `dotaws hook check` flow — already uses `eval`/`Invoke-Expression`
- **How it works**:
  1. `dotaws hook print --shell <shell>` already emits shell integration code. It will be extended to also define a `dotaws()` wrapper function.
  2. When the user types `dotaws login ...`, the shell function intercepts the call.
  3. For `login` subcommands: the function runs the real binary, captures the stdout output (export statements), and evaluates it in the current shell — setting env vars directly.
  4. For all other subcommands: the function passes through to the real binary unchanged.
  5. UX messages (confirm prompt, warnings, success) are printed to stderr by the Python CLI and remain visible to the user.
- **User setup**: Unchanged — user already adds `eval "$(dotaws hook print --shell <shell>)"` to their shell profile. The wrapper function is emitted as part of that snippet.
- **Alternatives considered**:
  - Print eval-ready script, require user to manually `eval "$(dotaws login)"`: Works but poor UX — the user must remember the `eval` wrapper every time, and the "Exported N variables" message is misleading since nothing is actually exported without `eval`. Rejected.
  - Direct `os.environ` mutation from Python: Only affects the Python process, not the parent shell. Rejected.
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
