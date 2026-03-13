# CLI Contract: dotaws

## Scope
Public command-line interface contract for cross-shell AWS login helper behavior.

## Command: `dotaws login`

### Purpose
Authenticate to AWS using selected profile (with MFA when required) and emit shell-safe environment activation output.

### Invocation
- Interactive: `dotaws login`
- Explicit profile: `dotaws login --profile <name>`
- Non-interactive safe mode: `dotaws login --profile <name> [--mfa-code <code>] --non-interactive`

### Inputs
- `--profile <name>` (optional): Explicit profile name; overrides `.aws_profile` marker when provided.
- `--mfa-code <code>` (optional): MFA token value for non-interactive workflows.
- `--shell <powershell|bash|zsh>` (optional): Force shell output format.
- `--non-interactive` (flag, optional): Disable prompts and require all needed inputs.
- `--format <shell|json>` (optional, default: `shell`): Output format.

### Behavioral Contract
1. If `--profile` is absent in interactive mode, command MUST present selectable profile list.
2. If selected/resolved profile requires MFA and no token supplied, command MUST prompt in interactive mode.
3. On success, output MUST include `AWS_PROFILE` and temporary credential variables when applicable.
4. Credentials MUST be for current shell session activation only; command MUST NOT persist temporary credentials to shared credential files.
5. In non-interactive mode with missing required inputs, command MUST return non-zero exit code with actionable guidance.

### Exit Codes
- `0`: Success.
- `2`: Usage/input error (missing required input in non-interactive mode, invalid flags).
- `3`: Profile resolution error (missing/invalid profile, malformed marker file).
- `4`: Authentication error (MFA invalid/expired, STS failure).
- `5`: Config error (malformed AWS config/credentials).
- `6`: Shell output generation error.

### Output Contract (`--format shell`)
Shell-safe assignment lines for target shell.

Required vars on success:
- `AWS_PROFILE`

Conditional vars (temporary credential session):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`
- `AWS_REGION` (if known)

Example (bash/zsh):
- `export AWS_PROFILE=dev`
- `export AWS_ACCESS_KEY_ID=...`

Example (PowerShell):
- `$env:AWS_PROFILE = "dev"`
- `$env:AWS_ACCESS_KEY_ID = "..."`

### Output Contract (`--format json`)
JSON object for automation:
- `status`: `ok|error`
- `profile`: resolved profile name
- `shell`: effective shell target
- `env`: map of env variable assignments (on success)
- `error`: object with `code`, `message`, `hint` (on failure)

## Command: `dotaws hook print`

### Purpose
Emit shell integration snippet for directory-change detection and `.aws_profile` confirm-before-auto-login behavior.

### Inputs
- `--shell <powershell|bash|zsh>` (required)

### Behavioral Contract
- MUST emit integration snippet for selected shell.
- Hook logic MUST detect nearest-parent `.aws_profile` on directory changes.
- Hook logic MUST request confirmation before auto-login.
- Hook logic MUST suppress repeated prompts in same shell session + directory context after decline.

### Exit Codes
- `0`: Success
- `2`: Invalid arguments
- `6`: Shell output generation error
