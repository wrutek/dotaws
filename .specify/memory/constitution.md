<!--
Sync Impact Report
- Version change: N/A (template) → 1.0.0
- Modified principles:
	- Template Principle 1 → I. Python-First, Typed, Modern
	- Template Principle 2 → II. CLI UX and Cross-Shell Compatibility
	- Template Principle 3 → III. Security by Default
	- Template Principle 4 → IV. Quality Gates (Non-Negotiable)
	- Template Principle 5 → V. Simplicity and Reliability
- Added sections:
	- Technical Standards
	- Delivery Workflow and Review
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ updated: .specify/templates/spec-template.md
	- ✅ updated: .specify/templates/tasks-template.md
	- ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
- Follow-up TODOs:
	- None
-->

# dotaws Constitution

## Core Principles

### I. Python-First, Typed, Modern
All production code MUST target Python 3.14 and use complete type hints for public
interfaces and core internal flows. Code MUST be modular, testable, and organized by
single responsibility. The standard library MUST be preferred first; third-party
dependencies MAY be added only when they provide clear, documented value that cannot
be met reasonably with the standard library.

Rationale: A modern typed Python baseline improves maintainability and predictability
for a cross-shell CLI with security-sensitive behavior.

### II. CLI UX and Cross-Shell Compatibility
The tool MUST provide consistent behavior across PowerShell and Bash/Zsh for core
commands, prompts, and outputs. It MUST support both interactive and non-interactive
modes. After successful login, it MUST emit shell-safe environment export data and
MUST set `AWS_PROFILE` in the active shell integration flow.

Rationale: The product promise is frictionless multi-shell AWS workflow automation.
Behavior drift across shells is a functional defect.

### III. Security by Default
The system MUST NOT persist credentials or MFA secrets in plaintext project files.
Authentication flows MUST minimize credential lifetime and prefer AWS-native
mechanisms for temporary credentials. Any auto-login trigger from `.aws_profile` MUST
require explicit user confirmation before credentials are activated.

Rationale: Local developer tooling still handles privileged cloud access and must
default to least-risk behavior.

### IV. Quality Gates (Non-Negotiable)
Every feature change MUST include automated tests for affected behavior. Core flows
(profile selection, MFA handling, `.aws_profile` auto-detect confirmation, and env
export including `AWS_PROFILE`) MUST be covered by integration and/or contract tests.
CI MUST run linting and static type checks, and merges MUST be blocked on failing
quality checks.

Rationale: Reliability for authentication tooling requires executable safeguards, not
manual spot checks.

### V. Simplicity and Reliability
Commands and configuration MUST remain minimal and explicit. Errors MUST be clear,
actionable, and user-oriented. Automation MUST be predictable and observable; hidden
state transitions or silent credential mutations are prohibited.

Rationale: A small tool remains trustworthy only when behavior is understandable and
repeatable.

## Technical Standards

The preferred implementation stack is Python 3.14 with: `typer` for CLI,
`rich` for terminal UX, `boto3`/`botocore` for AWS interactions, `pytest` for tests,
`ruff` for linting/formatting checks, and `mypy` for static type checks.

Dependency additions MUST include a brief justification in the relevant plan or pull
request and SHOULD be avoided when equivalent standard-library approaches are viable.

## Delivery Workflow and Review

Specifications MUST define interactive and non-interactive behavior, shell-specific
integration expectations, and security/error edge cases before implementation.

Implementation plans MUST include a Constitution Check with explicit pass/fail status
for each core principle before build work begins and after design decisions are made.

Task plans MUST include mandatory quality tasks for tests, lint, and type checks.
Feature completion requires passing automated checks and successful verification of
PowerShell and Bash/Zsh behavior for changed workflows.

## Governance

This constitution supersedes conflicting guidance in specs, plans, tasks, and local
workflow notes. Amendments MUST include: (1) rationale, (2) impact assessment on
templates and active work, and (3) semantic version update.

Versioning policy:
- MAJOR: Incompatible governance changes or principle removals/redefinitions.
- MINOR: New principle or materially expanded mandatory guidance.
- PATCH: Clarifications, wording improvements, and non-semantic refinements.

Compliance review policy:
- Every implementation plan and pull request MUST include a constitution compliance
	check.
- Non-compliant changes MUST be corrected before merge or explicitly approved via a
	documented amendment.

**Version**: 1.0.0 | **Ratified**: 2026-03-13 | **Last Amended**: 2026-03-13
