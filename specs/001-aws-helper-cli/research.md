# Research: Cross-Shell AWS Helper CLI

## Decision 1: CLI framework and terminal UX
- Decision: Use `typer` for command definition and `rich` for interactive terminal rendering.
- Rationale: Matches constitution recommendations, keeps UX clear, and supports maintainable command composition.
- Alternatives considered:
  - `argparse` only: lowest dependency count but poorer interactive UX and readability for profile selection.
  - `click` directly: solid option but `typer` provides cleaner typed command declarations for Python 3.14.

## Decision 2: AWS profile discovery compatibility
- Decision: Discover profiles through botocore/boto3 session config resolution (`~/.aws/config` and `~/.aws/credentials`) and preserve profile names exactly.
- Rationale: Aligns with Pulumi/AWS expectations and avoids custom parsing drift.
- Alternatives considered:
  - Manual INI parsing only: more error-prone and less compatible with future AWS profile semantics.
  - Separate profile registry file: violates compatibility and adds operational burden.

## Decision 3: MFA and temporary credential acquisition
- Decision: Use AWS STS-compatible flows via boto3/botocore, prompting for MFA when profile metadata requires it.
- Rationale: AWS-native mechanism minimizes security risk and respects existing IAM patterns.
- Alternatives considered:
  - External CLI subprocess wrappers only: introduces brittle parsing and less structured error handling.
  - Persisting cached credentials in project files: rejected for security and constitution compliance.

## Decision 4: Credential output and persistence model
- Decision: Export credentials to current shell session only; do not write temporary credentials to persistent plaintext stores.
- Rationale: Explicitly required by clarification and constitution security defaults.
- Alternatives considered:
  - Writing to AWS shared credentials file: easier reuse, but increases secret persistence risk.
  - Tool-managed encrypted cache: out of scope and adds complexity.

## Decision 5: Directory-entry auto-login trigger architecture
- Decision: Implement auto-detection through shell hooks (PowerShell prompt function; Bash/Zsh directory-change hooks such as `PROMPT_COMMAND`/`chpwd`).
- Rationale: Chosen clarification path; avoids background daemons and keeps behavior transparent.
- Alternatives considered:
  - Background watcher/daemon: extra process complexity and platform variance.
  - Wrapped `cd` alias only: lower reliability and easier to bypass accidentally.

## Decision 6: `.aws_profile` precedence and prompt suppression
- Decision: Explicit profile input overrides `.aws_profile`; prompt suppression tracked per shell session + directory context after decline.
- Rationale: Preserves user intent and avoids repetitive prompts without hidden global state.
- Alternatives considered:
  - `.aws_profile` always wins: surprising when explicit command intent is given.
  - Always re-prompt: degrades ergonomics.

## Decision 7: Non-interactive mode handling
- Decision: If required user interaction is missing in non-interactive mode, exit non-zero with actionable guidance.
- Rationale: deterministic automation behavior and explicit failure semantics.
- Alternatives considered:
  - Silent defaults: unsafe and ambiguous.
  - Blocking for input anyway: breaks CI/script execution.

## Decision 8: Testing strategy
- Decision: Use `pytest` with unit/integration/contract-style CLI tests and enforce `ruff` + `mypy` in CI.
- Rationale: Required by constitution quality gates; supports fast feedback for shell-specific behavior.
- Alternatives considered:
  - Unit tests only: insufficient coverage for shell behavior and auth workflows.
  - Manual QA only: non-repeatable and not gateable.
