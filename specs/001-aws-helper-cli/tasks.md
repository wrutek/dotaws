# Tasks: Cross-Shell AWS Helper CLI

**Input**: Design documents from /specs/001-aws-helper-cli/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Automated tests are REQUIRED for every story and changed behavior.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Python 3.14 CLI project and quality tooling.

- [X] T001 Initialize project metadata and dependencies in pyproject.toml
- [X] T002 Create source package scaffold in src/dotaws/__init__.py
- [X] T003 [P] Create CLI entrypoint wiring in src/dotaws/cli/app.py
- [X] T004 [P] Configure ruff rules in ruff.toml
- [X] T005 [P] Configure mypy settings in mypy.ini
- [X] T006 [P] Configure pytest defaults in pytest.ini
- [X] T007 [P] Create CI checks for tests, ruff, mypy in .github/workflows/ci.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared primitives required by all user stories.

**⚠️ CRITICAL**: No user story work starts before this phase completes.

- [X] T008 Create shared domain models in src/dotaws/shared/models.py
- [X] T009 [P] Create error taxonomy and exit code mapping in src/dotaws/shared/errors.py
- [X] T010 [P] Create terminal input/output helpers in src/dotaws/shared/io.py
- [X] T011 Implement shell detection utility in src/dotaws/shell/detection.py
- [X] T012 [P] Implement shell export renderer for PowerShell in src/dotaws/shell/powershell.py
- [X] T013 [P] Implement shell export renderer for Bash in src/dotaws/shell/bash.py
- [X] T014 [P] Implement shell export renderer for Zsh in src/dotaws/shell/zsh.py
- [X] T015 Implement credential export orchestration in src/dotaws/auth/credential_export.py
- [X] T016 Implement base command registration for login and hook commands in src/dotaws/cli/commands/__init__.py

**Checkpoint**: Foundation complete; story phases can proceed.

---

## Phase 3: User Story 1 - Interactive Profile Login (Priority: P1) 🎯 MVP

**Goal**: Provide interactive profile selection and successful login output with `AWS_PROFILE`.

**Independent Test**: Run `dotaws login`, select profile, verify shell-safe output and profile precedence behavior.

### Tests for User Story 1 (REQUIRED)

- [X] T017 [P] [US1] Add contract test for login command inputs/outputs in tests/contract/test_login_contract.py
- [X] T018 [P] [US1] Add integration test for interactive profile selection in tests/integration/test_login_interactive.py
- [X] T019 [P] [US1] Add integration test for explicit profile overriding .aws_profile in tests/integration/test_login_profile_precedence.py

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement AWS profile discovery service in src/dotaws/auth/profile_discovery.py
- [X] T021 [P] [US1] Implement login result presentation helpers in src/dotaws/cli/presenters/login_presenter.py
- [X] T022 [US1] Implement session acquisition service without MFA path in src/dotaws/auth/session_service.py
- [X] T023 [US1] Implement login command flow with interactive picker in src/dotaws/cli/commands/login.py
- [X] T024 [US1] Integrate credential export and `AWS_PROFILE` emission in src/dotaws/cli/commands/login.py
- [X] T025 [US1] Add JSON output mode for login command in src/dotaws/cli/commands/login.py

**Checkpoint**: US1 independently functional and demo-ready.

---

## Phase 4: User Story 2 - MFA Authentication Reliability (Priority: P2)

**Goal**: Support MFA challenge, retries, and clear failure guidance.

**Independent Test**: Run login with MFA-required profile; verify success for valid code and guided retries for invalid/expired code.

### Tests for User Story 2 (REQUIRED)

- [X] T026 [P] [US2] Add integration test for MFA success flow in tests/integration/test_login_mfa_success.py
- [X] T027 [P] [US2] Add integration test for invalid MFA retry guidance in tests/integration/test_login_mfa_retry.py
- [X] T028 [P] [US2] Add unit tests for MFA challenge handling in tests/unit/test_mfa.py

### Implementation for User Story 2

- [X] T029 [P] [US2] Implement MFA challenge service in src/dotaws/auth/mfa.py
- [X] T030 [US2] Extend session service for STS MFA path in src/dotaws/auth/session_service.py
- [X] T031 [US2] Add MFA prompt/retry flow to login command in src/dotaws/cli/commands/login.py
- [X] T032 [US2] Map MFA failure errors to exit code 4 and actionable hints in src/dotaws/shared/errors.py

**Checkpoint**: US1 and US2 work independently.

---

## Phase 5: User Story 3 - Project Auto-Login Prompt (Priority: P3)

**Goal**: Detect nearest `.aws_profile` on directory change and prompt before auto-login.

**Independent Test**: Enter project directories with marker files and verify confirmation, nearest-parent resolution, and decline suppression.

### Tests for User Story 3 (REQUIRED)

- [X] T033 [P] [US3] Add unit tests for marker parsing and nearest-parent resolution in tests/unit/test_profile_marker.py
- [X] T034 [P] [US3] Add integration test for confirm-before-auto-login behavior in tests/integration/test_auto_login_prompt.py
- [X] T035 [P] [US3] Add integration test for same-session decline suppression in tests/integration/test_auto_login_suppression.py

### Implementation for User Story 3

- [X] T036 [P] [US3] Implement `.aws_profile` discovery and parsing in src/dotaws/project/profile_marker.py
- [X] T037 [P] [US3] Implement per-session prompt suppression state in src/dotaws/project/prompt_state.py
- [X] T038 [US3] Implement hook snippet command in src/dotaws/cli/commands/hooks.py
- [X] T039 [US3] Implement auto-login trigger orchestration with confirmation in src/dotaws/cli/commands/hooks.py
- [X] T040 [US3] Handle invalid marker/profile errors with exit code 3 in src/dotaws/shared/errors.py

**Checkpoint**: US3 independently functional with shell hook flow.

---

## Phase 6: User Story 4 - Cross-Shell Consistency (Priority: P3)

**Goal**: Ensure equivalent behavior for PowerShell, Bash, and Zsh including non-interactive fail-fast rules.

**Independent Test**: Execute same workflows per shell and verify equivalent outputs and exit-code behavior.

### Tests for User Story 4 (REQUIRED)

- [X] T041 [P] [US4] Add contract test for hook print command in tests/contract/test_hook_contract.py
- [X] T042 [P] [US4] Add integration test for PowerShell export syntax in tests/integration/test_shell_powershell.py
- [X] T043 [P] [US4] Add integration test for Bash/Zsh export syntax in tests/integration/test_shell_posix.py
- [X] T044 [P] [US4] Add integration test for non-interactive missing-input fail-fast behavior in tests/integration/test_non_interactive_failfast.py

### Implementation for User Story 4

- [X] T045 [US4] Implement hook snippet generation for PowerShell in src/dotaws/shell/powershell.py
- [X] T046 [US4] Implement hook snippet generation for Bash in src/dotaws/shell/bash.py
- [X] T047 [US4] Implement hook snippet generation for Zsh in src/dotaws/shell/zsh.py
- [X] T048 [US4] Enforce non-interactive validation and exit code 2 path in src/dotaws/cli/commands/login.py
- [X] T049 [US4] Add shell-target selection logic for hook print command in src/dotaws/cli/commands/hooks.py

**Checkpoint**: All stories function equivalently across target shells.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Harden docs, packaging, and quality checks across all stories.

- [X] T050 [P] Add developer usage and shell setup docs in README.md
- [X] T051 [P] Align quickstart validation steps in specs/001-aws-helper-cli/quickstart.md
- [X] T052 [P] Add changelog entry for feature in CHANGELOG.md
- [X] T053 Run full test suite and fix regressions across tests/
- [X] T054 Run ruff and mypy and resolve final issues in src/dotaws/

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 → required before Phase 2.
- Phase 2 → blocks all user story phases.
- Phase 3 (US1) → MVP baseline.
- Phase 4 (US2), Phase 5 (US3), and Phase 6 (US4) depend on Phase 2; can proceed in parallel after MVP if staffed.
- Phase 7 depends on completion of targeted stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after foundational phase.
- **US2 (P2)**: Depends on US1 login baseline.
- **US3 (P3)**: Depends on foundational shell + login orchestration.
- **US4 (P3)**: Depends on core login and hook command paths from US1 and US3.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement models/services before command wiring.
- Complete story and validate independent test before moving on.

## Parallel Execution Examples

### User Story 1

- Run T017, T018, and T019 together.
- Run T020 and T021 together.

### User Story 2

- Run T026, T027, and T028 together.
- Run T029 in parallel with test execution prep.

### User Story 3

- Run T033, T034, and T035 together.
- Run T036 and T037 together.

### User Story 4

- Run T041, T042, T043, and T044 together.
- Run T045, T046, and T047 together.

## Implementation Strategy

### MVP First (US1)

1. Complete Setup (Phase 1).
2. Complete Foundational (Phase 2).
3. Deliver US1 (Phase 3) and validate MVP behavior.

### Incremental Delivery

1. Add US2 (MFA reliability).
2. Add US3 (project auto-login prompt).
3. Add US4 (cross-shell consistency and non-interactive guarantees).
4. Finish with polish and full quality-gate pass.
