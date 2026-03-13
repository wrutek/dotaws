# Feature Specification: Auto-Export Environment Variables

**Feature Branch**: `002-auto-export-env`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description: "Right now, the tool after logging just prints out env vars. I want them to be automatically exported to the shell but first asking user if they want to export them."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Login with Auto-Export (Priority: P1)

A user runs `dotaws login` in their shell. After successful authentication, instead of printing export statements for the user to copy-paste, the tool asks "Export credentials to current shell?" and, upon confirmation, sets the environment variables directly in the active shell session.

**Why this priority**: This is the core value of the feature — eliminating the manual copy-paste step that every user hits on every login.

**Independent Test**: Can be fully tested by running `dotaws login --profile <name>`, confirming the export prompt, and verifying that `$env:AWS_PROFILE` (PowerShell) or `echo $AWS_PROFILE` (Bash/Zsh) returns the expected value in the same shell session.

**Acceptance Scenarios**:

1. **Given** a user runs `dotaws login --profile myprofile` interactively, **When** authentication succeeds and the user confirms the export prompt (or presses Enter to accept the default Yes), **Then** the AWS environment variables are set in the current shell session and a success message is displayed.
2. **Given** a user runs `dotaws login --profile myprofile` interactively, **When** authentication succeeds and the user declines the export prompt, **Then** the export statements are printed to stdout (current behavior) so the user can copy-paste or pipe them manually.
3. **Given** a user runs `dotaws login` interactively with shell auto-detection, **When** authentication succeeds and the user confirms export, **Then** the variables are exported using the correct syntax for the detected shell (PowerShell, Bash, or Zsh).

---

### User Story 2 - Non-Interactive Mode Skips Prompt (Priority: P2)

A user runs `dotaws login --non-interactive --profile myprofile`. Since no human is present to confirm, the tool must skip the confirmation prompt entirely and fall back to printing the export statements (current behavior), preserving compatibility with scripts and automation.

**Why this priority**: Non-interactive mode is used in CI/CD and automation. Breaking it would be a regression.

**Independent Test**: Can be tested by running `dotaws login --non-interactive --profile <name>` and verifying that no prompt appears and export statements are printed to stdout.

**Acceptance Scenarios**:

1. **Given** a user runs `dotaws login --non-interactive --profile myprofile`, **When** authentication succeeds, **Then** the export statements are printed to stdout without any confirmation prompt (current behavior preserved).

---

### User Story 3 - JSON Output Mode Unaffected (Priority: P3)

A user runs `dotaws login --format json`. The JSON output mode is a machine-readable interface and must not be affected by the auto-export feature.

**Why this priority**: Preserving existing output contracts for tooling integrations.

**Independent Test**: Can be tested by running `dotaws login --format json --profile <name>` and verifying JSON output is unchanged.

**Acceptance Scenarios**:

1. **Given** a user runs `dotaws login --profile myprofile --format json`, **When** authentication succeeds, **Then** the output is JSON (unchanged from current behavior) with no export prompt.

---

### Edge Cases

- What happens when the user's shell cannot be detected? The tool should fall back to printing export statements and warn the user.
- What happens when the tool is piped (e.g., `dotaws login | grep AWS`)? The tool should detect non-TTY stdout and skip the confirmation prompt, printing export statements directly (pipe-friendly behavior).
- What happens in hook-triggered login (`dotaws hook check`)? The hook flow already uses `eval`/`Invoke-Expression` to apply exports, so it must remain unchanged.
- What happens when AWS env vars already exist in the shell? The tool warns which variables will be overwritten, then proceeds with the export (no second confirmation needed).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: After successful interactive login, the system MUST prompt the user with a confirmation question (default: Yes) before exporting environment variables to the shell.
- **FR-002**: If the user confirms, the system MUST set the environment variables (`AWS_PROFILE`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION`) directly in the current shell session.
- **FR-003**: If the user declines, the system MUST print the export statements to stdout (preserving current behavior).
- **FR-004**: In non-interactive mode (`--non-interactive`), the system MUST skip the confirmation prompt and print export statements to stdout.
- **FR-005**: In JSON output mode (`--format json`), the system MUST skip the confirmation prompt and output JSON (preserving current behavior).
- **FR-006**: When stdout is not a TTY (pipe or redirect), the system MUST skip the confirmation prompt and print export statements to stdout.
- **FR-007**: The auto-export mechanism MUST work correctly for PowerShell, Bash, and Zsh.
- **FR-008**: The shell hook flow (`dotaws hook check`) MUST remain unchanged — it already applies exports via eval/Invoke-Expression.
- **FR-009**: After successful export, the system MUST display a brief success confirmation (e.g., profile name and number of variables set).
- **FR-010**: If AWS environment variables already exist in the current shell, the system MUST warn the user which variables will be overwritten before proceeding with the export (no second confirmation required).

### Key Entities

- **ShellExportPayload**: Already exists — contains the shell type, env map, and rendered script. Used to drive both the print and direct-export paths.
- **InvocationMode**: Already exists — `INTERACTIVE` vs `NON_INTERACTIVE`. Used to decide whether to show the confirmation prompt.

## Assumptions

- The direct-export mechanism for Bash/Zsh will use the existing eval-based pattern (outputting shell commands that are eval'd by a wrapper). A pure subprocess cannot set variables in its parent shell — the same approach used by the hook flow will be reused for login.
- For PowerShell, the existing `Invoke-Expression` pattern from hooks is the mechanism.
- The confirmation prompt uses the existing `ask_confirm` helper from `dotaws.shared.io`.
- TTY detection uses standard `sys.stdout.isatty()` to determine if the output is interactive.

## Constitution Alignment *(mandatory)*

- **Python & Typing**: All new code will target Python 3.14 with full type hints. No `from __future__ import annotations` needed.
- **Cross-Shell UX**: The auto-export mechanism must produce correct syntax for all three shells (PowerShell, Bash, Zsh) and the confirmation prompt must work identically across all of them.
- **Security Defaults**: Credentials are only exported to the current session after explicit user confirmation. No credentials are persisted to disk. The confirmation step reinforces the user's awareness of credential scope.
- **Quality Gates**: New tests must cover the confirm/decline paths, non-interactive bypass, JSON bypass, and pipe/non-TTY bypass. ruff, mypy, and pytest must all pass.
- **Simplicity & Reliability**: The feature adds one decision point (confirm/decline) to the existing login flow. The export mechanism reuses the existing shell renderers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can authenticate and have credentials active in their shell in a single command without any copy-paste step.
- **SC-002**: The confirmation prompt adds no more than one additional user interaction (yes/no) to the login flow.
- **SC-003**: Existing non-interactive and JSON workflows continue to work identically with no changes required by users.
- **SC-004**: All three shells (PowerShell, Bash, Zsh) correctly receive exported variables after user confirmation.
- **SC-005**: When stdout is piped or redirected, the tool produces clean, parseable export statements with no interactive prompts.

## Clarifications

### Session 2026-03-13

- Q: What should the default answer be when the user presses Enter on the export confirmation prompt? → A: Default Yes — pressing Enter exports immediately (lowest friction).
- Q: What should happen when AWS env vars already exist from a previous session? → A: Warn then overwrite — show which vars will be replaced, then proceed without a second confirmation.
