# Implementation Plan: Cross-Shell AWS Helper CLI

**Branch**: `001-aws-helper-cli` | **Date**: 2026-03-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-aws-helper-cli/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a Python 3.14 CLI that streamlines AWS login across PowerShell and Bash/Zsh
with interactive profile selection, MFA handling, shell-safe environment exports,
and `.aws_profile`-driven auto-login prompts on directory changes. The technical
approach uses AWS shared config compatibility, STS-backed temporary sessions,
shell-hook-based directory detection, and session-only credential export.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.14  
**Primary Dependencies**: typer, rich, boto3/botocore, uv, pytest, mypy, ruff  
**Storage**: N/A (ephemeral in-memory state; reads AWS shared config/credentials and project `.aws_profile`)  
**Testing**: pytest (unit + integration + contract-style CLI behavior tests)  
**Target Platform**: PowerShell on Windows; Bash/Zsh on macOS/Linux  
**Project Type**: CLI tool  
**Performance Goals**: Interactive profile list render <1s for <=100 profiles; login flow completes within user-driven target of <=30s in normal network conditions  
**Constraints**: Session-only credential export; no plaintext credential persistence by tool; explicit confirmation for `.aws_profile` auto-login; non-interactive prompt-required flows must fail fast with non-zero exit  
**Scale/Scope**: Single-user local developer workflow; dozens of profiles per machine; repeated project directory switches in one shell session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Python 3.14 + typed design: language version pinned; type strategy defined.
- [x] Cross-shell UX parity: PowerShell and Bash/Zsh behavior mapped.
- [x] Security defaults: no plaintext secrets; explicit `.aws_profile` confirmation.
- [x] Quality gates: tests for changed behavior, lint, and type checks planned.
- [x] Simplicity: minimal commands/config; no hidden credential state transitions.

Gate Result (pre-research): PASS

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
└── dotaws/
  ├── cli/
  │   ├── app.py
  │   ├── commands/
  │   │   ├── login.py
  │   │   └── hooks.py
  │   └── presenters/
  ├── auth/
  │   ├── profile_discovery.py
  │   ├── mfa.py
  │   ├── session_service.py
  │   └── credential_export.py
  ├── project/
  │   ├── profile_marker.py
  │   └── prompt_state.py
  ├── shell/
  │   ├── detection.py
  │   ├── powershell.py
  │   ├── bash.py
  │   └── zsh.py
  └── shared/
    ├── models.py
    ├── errors.py
    └── io.py

tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: Single-project Python CLI structure with domain-separated
modules for auth, shell integration, project marker resolution, and CLI presentation.
This keeps behavior explicit and testable while matching constitution simplicity
constraints.

## Post-Design Constitution Check

- [x] Python 3.14 + typed design reflected in module and contract design.
- [x] Cross-shell parity captured in CLI contract and quickstart shell-specific hook flows.
- [x] Security defaults preserved: confirm-before-auto-login and session-only credential export.
- [x] Quality gates included in plan outputs (research decisions + testing strategy).
- [x] Simplicity maintained via single CLI surface and no background daemons.

Gate Result (post-design): PASS

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
