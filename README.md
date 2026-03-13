# dotaws

Cross-shell AWS helper CLI for PowerShell, Bash, and Zsh.

## Features
- Interactive AWS profile selection (`dotaws login`)
- MFA-aware authentication flow
- Session-only environment export including `AWS_PROFILE`
- `.aws_profile` directory marker support with confirmation
- Shell hook snippet generation (`dotaws hook print`)

## Install

### From GitHub (no clone needed)

```bash
# Run directly without installing
uvx --from git+https://github.com/wrutek/dotaws dotaws --help

# Install as a global tool
uv tool install git+https://github.com/wrutek/dotaws
```

### From source (development)

```bash
git clone git@github.com:wrutek/dotaws.git
cd dotaws
uv sync --dev
uv run dotaws --help
```

### Requirements
- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Commands
- `dotaws login [--profile NAME] [--mfa-code CODE] [--shell powershell|bash|zsh] [--non-interactive] [--format shell|json]`
- `dotaws hook print --shell powershell|bash|zsh`
- `dotaws hook check --shell powershell|bash|zsh`

## Shell Setup
Generate hook snippet and add it to your shell profile:
- PowerShell: `dotaws hook print --shell powershell`
- Bash: `dotaws hook print --shell bash`
- Zsh: `dotaws hook print --shell zsh`

## Notes
- Explicit `--profile` always overrides `.aws_profile`.
- In non-interactive mode, required missing inputs fail fast with non-zero exit.
- Temporary credentials are not persisted by this tool.
