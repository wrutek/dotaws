# Data Model: Cross-Shell AWS Helper CLI

## Entity: AWSProfileContext
- Purpose: Represents a discovered AWS profile and auth requirements.
- Fields:
  - `name` (string, required)
  - `source` (enum: `config`, `credentials`, `merged`; required)
  - `region` (string, optional)
  - `role_arn` (string, optional)
  - `source_profile` (string, optional)
  - `mfa_serial` (string, optional)
  - `requires_mfa` (boolean, derived)
- Validation rules:
  - `name` must be non-empty.
  - `requires_mfa` is true when `mfa_serial` is present or profile chain requires MFA.

## Entity: AuthRequest
- Purpose: Captures login request inputs and execution mode.
- Fields:
  - `requested_profile` (string, optional)
  - `resolved_profile` (string, required)
  - `invocation_mode` (enum: `interactive`, `non_interactive`; required)
  - `trigger` (enum: `manual_login`, `dir_auto_prompt`; required)
  - `cwd` (string path, optional)
- Validation rules:
  - `resolved_profile` must refer to discovered profile.
  - If `invocation_mode=non_interactive`, all required inputs must be pre-supplied.

## Entity: MFACodeChallenge
- Purpose: Tracks MFA prompt and validation attempts.
- Fields:
  - `profile_name` (string, required)
  - `mfa_serial` (string, required when challenge exists)
  - `attempt_count` (integer, required, >= 0)
  - `last_error_code` (string, optional)
- Validation rules:
  - Maximum retry count is implementation-defined but must produce actionable error on failure.

## Entity: AuthenticatedSession
- Purpose: Represents temporary authenticated AWS credentials and metadata.
- Fields:
  - `profile_name` (string, required)
  - `access_key_id` (string, required)
  - `secret_access_key` (string, required)
  - `session_token` (string, required for temp creds)
  - `expiration` (datetime, optional)
  - `region` (string, optional)
  - `aws_profile` (string, required)
- Validation rules:
  - `aws_profile` must equal `profile_name` for exported context.
  - Expired sessions are invalid for export.

## Entity: ShellExportPayload
- Purpose: Shell-specific environment export output.
- Fields:
  - `shell` (enum: `powershell`, `bash`, `zsh`; required)
  - `env` (map<string,string>, required)
  - `script` (string, required)
- Validation rules:
  - Must always include `AWS_PROFILE` after successful login.
  - Must include temporary credential variables when present.

## Entity: ProjectProfileMarker
- Purpose: Represents nearest `.aws_profile` marker resolution.
- Fields:
  - `file_path` (string path, required)
  - `directory` (string path, required)
  - `profile_name` (string, required)
  - `depth_from_cwd` (integer, required, >= 0)
- Validation rules:
  - Nearest-parent marker wins if multiple markers exist.
  - Empty or malformed marker is treated as invalid marker error.

## Entity: PromptSuppressionState
- Purpose: Tracks declined auto-login prompts for current shell session.
- Fields:
  - `session_id` (string, required)
  - `directory_key` (string canonical path, required)
  - `suppressed_profile` (string, required)
  - `suppressed_at` (datetime, required)
- Validation rules:
  - Suppression applies only within current shell session.
  - Suppression resets when directory context changes.

## Relationships
- `AuthRequest.resolved_profile` -> `AWSProfileContext.name`
- `MFACodeChallenge.profile_name` -> `AWSProfileContext.name`
- `AuthenticatedSession.profile_name` -> `AWSProfileContext.name`
- `ShellExportPayload.env[AWS_PROFILE]` <- `AuthenticatedSession.aws_profile`
- `ProjectProfileMarker.profile_name` -> `AWSProfileContext.name` (must resolve before auto-login)
- `PromptSuppressionState.directory_key` relates to `ProjectProfileMarker.directory`

## State Transitions
1. `AuthRequest` created -> profile resolved from explicit input or discovery.
2. If profile requires MFA: `MFACodeChallenge` enters `pending` -> `validated` or `failed`.
3. On successful auth: `AuthenticatedSession` enters `active` -> may become `expired`.
4. On export: `ShellExportPayload` generated and emitted to active shell.
5. On directory enter with marker: auto-login prompt shown -> `accepted` (auth flow continues) or `declined` (create `PromptSuppressionState`).
