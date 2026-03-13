# Feature Specification: Cross-Shell AWS Helper CLI

**Feature Branch**: `001-aws-helper-cli`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description: "Build a small cross-shell AWS helper CLI focused on developer ergonomics with profile selection, MFA, `.aws_profile` auto-detect confirmation, and shell env export including `AWS_PROFILE` using Python 3.14"

## Clarifications

### Session 2026-03-13

- Q: For project auto-login on directory enter, which trigger model should the spec require? → A: Shell hook integration on directory change (PowerShell prompt function, Bash/Zsh `PROMPT_COMMAND`/`chpwd`).
- Q: For authenticated credentials handling, what should be required by default? → A: Export credentials to current shell session only (no credential file writes by this tool).
- Q: If both an explicit profile is provided and a `.aws_profile` marker is found, which should take precedence? → A: Explicit user-provided profile takes precedence.
- Q: In non-interactive mode, if login needs user input (profile pick, MFA, or auto-login confirmation), what should happen? → A: Exit with non-zero code and clear message explaining required flags/inputs.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Interactive Profile Login (Priority: P1)

As a developer, I run `login`, choose an AWS profile from an interactive list, and immediately get a usable authenticated shell context.

**Why this priority**: This is the primary value proposition and minimum usable workflow.

**Independent Test**: Can be fully tested by running `login` in an interactive shell, selecting a profile, and verifying exported environment values are usable for AWS CLI commands.

**Acceptance Scenarios**:

1. **Given** multiple configured AWS profiles, **When** the user runs `login` without explicit profile input, **Then** the system shows a selectable profile list and proceeds with the selected profile.
2. **Given** successful authentication, **When** login completes, **Then** the shell activation output includes `AWS_PROFILE` and any required temporary credential variables.
3. **Given** an explicit profile argument and a detected `.aws_profile` marker, **When** `login` is executed, **Then** the explicit profile is used.

---

### User Story 2 - MFA Authentication Reliability (Priority: P2)

As a developer using MFA-protected profiles, I can enter a token and complete login with clear guidance when MFA validation fails.

**Why this priority**: MFA support is required in many real AWS environments and blocks adoption without reliable handling.

**Independent Test**: Can be tested by using an MFA-required profile, entering valid and invalid token codes, and confirming successful auth or actionable retry feedback.

**Acceptance Scenarios**:

1. **Given** a selected profile that requires MFA, **When** the user enters a valid MFA code, **Then** the system establishes a valid temporary session and completes login.
2. **Given** a selected profile that requires MFA, **When** the user enters an invalid or expired MFA code, **Then** the system reports the issue clearly and allows retry without requiring a full restart.

---

### User Story 3 - Project Auto-Login Prompt (Priority: P3)

As a developer switching projects, entering a directory containing `.aws_profile` prompts me to confirm auto-login for that project profile.

**Why this priority**: This removes repetitive manual context switching while preserving user control.

**Independent Test**: Can be tested by entering a directory with `.aws_profile`, confirming prompt behavior, validating login on approval, and verifying suppression behavior after decline.

**Acceptance Scenarios**:

1. **Given** a project directory with `.aws_profile`, **When** the shell session enters that directory, **Then** the system asks for confirmation before auto-login.
2. **Given** the user declines the prompt, **When** they remain in the same directory context, **Then** the system does not repeatedly prompt during that session.
3. **Given** multiple nested `.aws_profile` files, **When** the user enters a nested path, **Then** the nearest parent marker is used.

---

### User Story 4 - Cross-Shell Consistency (Priority: P3)

As a cross-platform user, I receive equivalent behavior and clear instructions in PowerShell, Bash, and Zsh.

**Why this priority**: Consistent UX prevents shell-specific surprises and support burden.

**Independent Test**: Can be tested by executing the same login and auto-profile workflows in each target shell and comparing outcomes.

**Acceptance Scenarios**:

1. **Given** a supported shell, **When** login succeeds, **Then** the activation output is valid for that shell and produces an equivalent authenticated environment.
2. **Given** non-interactive execution, **When** prompt-required flows are triggered, **Then** the system exits safely with clear guidance instead of hanging.

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- `.aws_profile` references a profile name that does not exist.
- `.aws_profile` exists but is empty, malformed, or unreadable.
- MFA challenge succeeds initially but credentials expire during a later command.
- AWS config/credentials files are malformed or partially corrupted.
- Non-interactive shell execution cannot complete a required prompt flow.
- User repeatedly enters a project directory after declining auto-login in the same shell session.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The system MUST provide a `login` command that supports interactive profile selection when no explicit profile is provided.
- **FR-002**: The system MUST discover available AWS profiles from standard AWS shared configuration and credentials sources used by typical Pulumi workflows.
- **FR-003**: The system MUST allow users to select one discovered profile and continue authentication with that profile context.
- **FR-004**: The system MUST support MFA authentication flows for profiles that require MFA.
- **FR-005**: The system MUST provide clear retry guidance for invalid or expired MFA codes.
- **FR-006**: After successful login, the system MUST set `AWS_PROFILE` in the shell activation output.
- **FR-007**: After successful login with temporary credentials, the system MUST expose required temporary credential environment values for the active shell.
- **FR-007**: After successful login with temporary credentials, the system MUST expose required temporary credential environment values for the active shell session only.
- **FR-008**: The system MUST provide shell-appropriate activation output for PowerShell and Bash/Zsh.
- **FR-009**: The system MUST detect `.aws_profile` in the current directory or nearest parent directory and read the profile name from it.
- **FR-010**: The system MUST ask for explicit user confirmation before executing auto-login triggered by `.aws_profile`.
- **FR-011**: If the user declines auto-login, the system MUST suppress repeated prompts for the same directory context within the same shell session.
- **FR-015**: Directory-entry auto-detection MUST be implemented via shell hook integration (PowerShell prompt function and Bash/Zsh directory-change hooks) rather than background watchers.
- **FR-016**: The tool MUST NOT write authenticated temporary credentials to AWS shared credentials files or other persistent plaintext stores.
- **FR-017**: When both an explicit profile input and `.aws_profile` are present, the explicit profile input MUST take precedence.
- **FR-012**: The system MUST continue to work with existing AWS and Pulumi profile workflows without modifying user profile definitions.
- **FR-013**: The system MUST fail safely with clear user-facing messages for invalid profile names, malformed AWS config data, and non-interactive prompt-required scenarios.
- **FR-014**: The system MUST avoid persisting secrets in plaintext project files.
- **FR-018**: In non-interactive mode, when required user input is missing, the command MUST exit with a non-zero status and provide actionable guidance for supplying required inputs.

### Key Entities *(include if feature involves data)*

- **AWS Profile Context**: Represents a selectable profile name, source metadata, and whether MFA is required.
- **Authenticated Session**: Represents temporary credential state, expiration, and shell export payload.
- **Project Profile Marker**: Represents `.aws_profile` location, parsed profile name, and nearest-parent resolution result.
- **Shell Session Prompt State**: Represents per-session suppression state for declined auto-login prompts by directory context.

## Assumptions

- Users already have valid AWS profile configuration locally.
- Shell integration hooks for directory-entry behavior can be installed by users per shell documentation.
- Directory-entry detection relies on shell-native hooks (PowerShell prompt customization and Bash/Zsh prompt or directory-change hooks).
- Local shell sessions are trusted contexts for temporary environment variable exports.
- The tool exports credentials for current shell session scope only; persistence is outside feature scope.

## Dependencies

- Access to AWS identity services needed for profile authentication and MFA challenge resolution.
- Read access to local AWS shared config/credentials files.
- Shell support for evaluating generated activation output.

## Out of Scope

- GUI or browser-based flows.
- Full secret vault or long-term credential storage management.
- Multi-cloud workflows beyond AWS.

## Constitution Alignment *(mandatory)*

- **Python & Typing**: Implementation is constrained to a Python 3.14 codebase with typed interfaces and testable modular components.
- **Cross-Shell UX**: Feature requires equivalent login, MFA, auto-profile prompt, and env activation outcomes across PowerShell and Bash/Zsh.
- **Security Defaults**: Explicit confirmation before `.aws_profile` auto-login is mandatory; no plaintext secret persistence is allowed.
- **Quality Gates**: Automated tests must cover profile selection, MFA flow, auto-login confirmation behavior, and shell env export including `AWS_PROFILE`; lint and type checks are required.
- **Simplicity & Reliability**: Scope remains CLI-first with minimal config surface and clear actionable error handling.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: In usability tests, at least 90% of users complete login with profile selection in under 30 seconds on first attempt.
- **SC-002**: For MFA-required profiles, at least 95% of valid MFA attempts result in successful authenticated sessions without restarting the command.
- **SC-003**: In shell compatibility checks, 100% of core flows (interactive login, MFA login, `.aws_profile` confirm-before-auto-login, env activation output) pass in PowerShell and Bash/Zsh.
- **SC-004**: After rollout, users report at least a 40% reduction in manual AWS context-switch steps per project switch.
- **SC-005**: 100% of failure paths for invalid profile, MFA failure, malformed AWS config, and non-interactive prompt-required mode return clear actionable guidance.
- **SC-006**: In automated non-interactive tests, 100% of prompt-required invocations fail fast with non-zero exit status and documented remediation guidance.
