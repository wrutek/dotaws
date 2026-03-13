# Implementation Plan: Auto-Export Environment Variables

**Branch**: `002-auto-export-env` | **Date**: 2026-03-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-auto-export-env/spec.md`

**Note**: Minimal-change plan — modifies only login.py and io.py; no new files, no new dependencies.

## Summary

After successful interactive login, instead of only printing shell export statements, the tool asks the user whether to export credentials directly to the current shell. On confirmation, it outputs eval-ready commands; on decline, it prints the export script as before. Non-interactive mode, JSON format, and piped stdout all bypass the prompt and preserve current behavior.

## Technical Context

**Language/Version**: Python 3.14  
**Primary Dependencies**: typer, rich, boto3/botocore (all existing — no additions)  
**Storage**: N/A  
**Testing**: pytest (existing)  
**Target Platform**: Windows (PowerShell), Linux/macOS (Bash, Zsh)  
**Project Type**: CLI  
**Performance Goals**: N/A (interactive CLI)  
**Constraints**: Cannot set parent shell env vars from a subprocess — must output eval-ready script  
**Scale/Scope**: ~30 lines of changes across 2 existing files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Python 3.14 + typed design: All changes in Python 3.14, full type hints on new/modified functions.
- [x] Cross-shell UX parity: Confirmation prompt works identically in all shells; export scripts already shell-specific.
- [x] Security defaults: Export requires explicit user confirmation (default: Yes). Overwrite of existing vars triggers a warning.
- [x] Quality gates: Tests for confirm, decline, non-interactive bypass, JSON bypass, pipe/non-TTY bypass.
- [x] Simplicity: One new branch in the existing `login()` function. No new commands, no new config.

## Project Structure

### Documentation (this feature)

```text
specs/002-auto-export-env/
├── plan.md              # This file
├── research.md          # Phase 0 (trivial — no unknowns)
├── data-model.md        # Phase 1 (no new entities)
├── quickstart.md        # Phase 1
└── contracts/           # Phase 1 (CLI contract delta)
```

### Source Code Changes (minimal)

```text
src/dotaws/
├── cli/commands/login.py    # MODIFY: add confirm/warn/export logic after auth
└── shared/io.py             # MODIFY: add print_warning helper

tests/
├── integration/test_login_auto_export.py   # NEW: confirm, decline, overwrite-warn paths
└── integration/test_login_interactive.py   # EXISTING: may need minor adjustment
```

**Structure Decision**: No new modules or packages. The feature is a behavioral change in the existing `login()` function, with one new test file.

## Complexity Tracking

No violations. No complexity additions.
