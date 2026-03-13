# Quickstart: Cross-Shell AWS Helper CLI

## Prerequisites
- Python 3.14
- AWS profiles configured in shared AWS config/credentials
- MFA device configured for MFA-protected profiles

## Install (development)
1. Create and activate a Python environment.
2. Install package and dev dependencies.
3. Verify command is available as `dotaws`.

## Manual Login Flow
1. Run `dotaws login`.
2. Select profile from interactive list.
3. If prompted, enter MFA code.
4. Evaluate emitted shell output in current shell session.
5. Validate context with an AWS command (for example, caller identity).

## Explicit Profile Login
- Run `dotaws login --profile <profile-name>`.
- If both explicit profile and `.aws_profile` are present, explicit profile is used.

## Non-Interactive Usage
- Use `dotaws login --profile <name> --non-interactive`.
- If MFA is required, also pass `--mfa-code <code>`.
- Missing required inputs returns non-zero exit and actionable guidance.

## Enable Directory-Change Auto Prompt
Generate and install hook snippet for your shell:
- PowerShell: `dotaws hook print --shell powershell`
- Bash: `dotaws hook print --shell bash`
- Zsh: `dotaws hook print --shell zsh`

Behavior after hook install:
1. On directory change, nearest-parent `.aws_profile` is detected.
2. User is asked to confirm auto-login.
3. If declined, prompt is suppressed for same session + directory context.

## `.aws_profile` Format
- Plain text containing a single profile name, e.g.:
  - `dev-admin`

## Validation Checklist
- Interactive profile selection works.
- MFA profile authentication succeeds.
- `AWS_PROFILE` is present after successful login.
- Temporary credential env vars are exported for session-only use.
- Invalid profile and malformed config errors are clear.
- PowerShell and Bash/Zsh flows produce equivalent outcomes.
