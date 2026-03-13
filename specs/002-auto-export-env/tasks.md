# Tasks: Auto-Export Environment Variables

**Input**: Design documents from `/specs/002-auto-export-env/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Automated tests are REQUIRED for every feature change. Test tasks are included for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add shared helpers needed by all user stories

- [X] T001 Add `print_warning(message: str) -> None` helper in src/dotaws/shared/io.py
- [X] T002 Add `_check_existing_env_vars(env: dict[str, str]) -> list[str]` helper in src/dotaws/cli/commands/login.py

**Checkpoint**: Shared helpers available for user story implementation

---

## Phase 2: User Story 1 - Interactive Login with Auto-Export (Priority: P1) 🎯 MVP

**Goal**: After successful interactive login, prompt user to export credentials; on confirm, output eval-ready script + success message; on decline, print export statements (current behavior). Warn if existing AWS vars will be overwritten.

**Independent Test**: Run `dotaws login --profile <name>`, confirm prompt, verify env vars are set in shell.

### Tests for User Story 1 (REQUIRED) ✅

- [X] T003 [P] [US1] Integration test: user confirms export → eval-ready script printed + success message, in tests/integration/test_login_auto_export.py
- [X] T004 [P] [US1] Integration test: user declines export → raw export statements printed (current behavior), in tests/integration/test_login_auto_export.py
- [X] T005 [P] [US1] Integration test: existing AWS env vars detected → overwrite warning printed before export, in tests/integration/test_login_auto_export.py

### Implementation for User Story 1

- [X] T006 [US1] Refactor `login()` in src/dotaws/cli/commands/login.py to add confirm/decline branch after `execute_login()` for interactive + TTY + shell-format path: prompt with `ask_confirm("Export credentials to current shell?", default=True)`, on confirm check for existing vars via `_check_existing_env_vars()`, warn if any, print eval-ready script + success message; on decline print raw script (current behavior)
- [X] T007 [US1] Verify all three shells produce correct output: PowerShell (`$env:X = "V"`), Bash (`export X='V'`), Zsh (`export X='V'`) — extend existing test or add shell-specific assertions in tests/integration/test_login_auto_export.py

**Checkpoint**: User Story 1 fully functional — interactive login with auto-export works

---

## Phase 3: User Story 2 - Non-Interactive Mode Skips Prompt (Priority: P2)

**Goal**: `--non-interactive` flag bypasses the new confirmation prompt entirely, preserving current behavior.

**Independent Test**: Run `dotaws login --non-interactive --profile <name>` and verify no prompt, export statements printed.

### Tests for User Story 2 (REQUIRED) ✅

- [X] T008 [P] [US2] Integration test: non-interactive mode skips prompt and prints export statements directly, in tests/integration/test_login_auto_export.py

### Implementation for User Story 2

- [X] T009 [US2] Ensure `login()` in src/dotaws/cli/commands/login.py checks `non_interactive` flag before showing prompt — if True, print result directly (current behavior); this should be part of the condition guard added in T006

**Checkpoint**: Non-interactive mode verified — no regression

---

## Phase 4: User Story 3 - JSON Output Mode Unaffected (Priority: P3)

**Goal**: `--format json` bypasses the confirmation prompt and outputs JSON as before.

**Independent Test**: Run `dotaws login --format json --profile <name>` and verify unchanged JSON output.

### Tests for User Story 3 (REQUIRED) ✅

- [X] T010 [P] [US3] Integration test: JSON format skips prompt and outputs JSON unchanged, in tests/integration/test_login_auto_export.py

### Implementation for User Story 3

- [X] T011 [US3] Ensure `login()` in src/dotaws/cli/commands/login.py checks `format == "json"` before showing prompt — if json, print result directly (current behavior); this should be part of the condition guard added in T006

**Checkpoint**: JSON output mode verified — no regression

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, quality gates, and pipe/TTY handling

- [X] T012 [P] Integration test: piped stdout (non-TTY) skips prompt and prints export statements, in tests/integration/test_login_auto_export.py
- [X] T013 Ensure `login()` in src/dotaws/cli/commands/login.py checks `sys.stdout.isatty()` in the condition guard — if not TTY, print result directly
- [X] T014 [P] Verify `dotaws hook check` flow is unchanged — run existing hook tests in tests/contract/test_hook_contract.py
- [X] T015 Run quality gates: `uv run ruff check .`, `uv run mypy src/`, `uv run pytest tests/ -q`
- [X] T016 Run quickstart.md validation scenarios manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Story 1 (Phase 2)**: Depends on Phase 1 completion
- **User Story 2 (Phase 3)**: Depends on Phase 2 (the condition guard in T006 handles both)
- **User Story 3 (Phase 4)**: Depends on Phase 2 (same condition guard)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup — the core feature
- **User Story 2 (P2)**: Logically part of the same condition guard as US1; add test + verify
- **User Story 3 (P3)**: Same — add test + verify JSON path

### Parallel Opportunities

- T003, T004, T005 can all run in parallel (separate test functions, same file)
- T008, T010, T012 can all run in parallel with each other
- T001 and T002 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch all tests in parallel:
T003: "Integration test: user confirms export"
T004: "Integration test: user declines export"  
T005: "Integration test: overwrite warning"

# Then implement:
T006: "Refactor login() with confirm/decline branch"
T007: "Verify shell-specific output"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: User Story 1 (T003–T007)
3. **STOP and VALIDATE**: Test auto-export interactively
4. All value is delivered — remaining phases are regression guards

### Incremental Delivery

1. Setup → Helpers ready
2. User Story 1 → Core auto-export working (MVP!)
3. User Story 2 → Non-interactive regression verified
4. User Story 3 → JSON regression verified
5. Polish → Edge cases, quality gates, final validation

---

## Notes

- All changes are in 2 existing files: `src/dotaws/cli/commands/login.py` and `src/dotaws/shared/io.py`
- 1 new test file: `tests/integration/test_login_auto_export.py`
- The condition guard in T006 is the single branching point — US2 and US3 are primarily test-only phases
- No new dependencies, no new modules, no new commands
- Commit after each phase for clean git history
