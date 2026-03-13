# CLI Contract Delta: Auto-Export Environment Variables

**Feature**: 002-auto-export-env  
**Date**: 2026-03-13

## Mechanism: Shell Wrapper Function

The `dotaws hook print` snippet (already sourced in the user's shell profile) is extended to define a `dotaws()` shell wrapper function. This function intercepts `dotaws login` calls, runs the real binary, and **evaluates the export output directly in the current shell** — setting environment variables in the parent process without requiring the user to wrap calls in `eval`.

For all other subcommands, the wrapper passes through to the real binary unchanged.

## Changed Command: `dotaws login`

### Before (current behavior)

```
$ dotaws login --profile myprofile
export AWS_PROFILE='myprofile'
export AWS_ACCESS_KEY_ID='ASIA...'
export AWS_SECRET_ACCESS_KEY='...'
export AWS_SESSION_TOKEN='...'
```

Prints export statements to stdout. User must copy-paste or wrap in `eval` — variables are **not** set in the current shell.

### After (new behavior)

#### Interactive + TTY + shell format:

```
$ dotaws login --profile myprofile
Export credentials to current shell? [Y/n]: y
⚠ Overwriting: AWS_PROFILE, AWS_ACCESS_KEY_ID    # only if vars already exist
✓ Exported 4 variables for profile 'myprofile'
```

The shell wrapper function evaluates the export statements emitted by the CLI. Variables **are set directly in the current shell session**. No `eval` wrapper needed.

If user declines:

```
$ dotaws login --profile myprofile
Export credentials to current shell? [Y/n]: n
export AWS_PROFILE='myprofile'
export AWS_ACCESS_KEY_ID='ASIA...'
export AWS_SECRET_ACCESS_KEY='...'
export AWS_SESSION_TOKEN='...'
```

Falls back to printing export statements without applying them (current behavior).

#### Non-interactive / piped (via shell wrapper):

```
$ dotaws login --profile myprofile --non-interactive
```

Shell wrapper detects `--non-interactive` or non-TTY stdout and **applies the exports directly** (no prompt). Variables are set in the current shell.

#### JSON format: Unchanged (no auto-export)

```
$ dotaws login --profile myprofile --format json
{"status": "ok", "profile": "myprofile", ...}
```

JSON output is printed to stdout as-is; the wrapper does **not** eval JSON output.

### Changed Command: `dotaws hook print`

The emitted shell integration snippet now includes a `dotaws()` wrapper function in addition to the existing directory-change hook.

#### Bash/Zsh wrapper (emitted as part of hook snippet):

```bash
dotaws() {
  if [ "$1" = "login" ]; then
    local output
    output="$(command dotaws "$@")"
    local rc=$?
    if [ $rc -eq 0 ] && [ -n "$output" ]; then
      eval "$output"
    fi
    return $rc
  fi
  command dotaws "$@"
}
```

#### PowerShell wrapper (emitted as part of hook snippet):

```powershell
function dotaws {
  if ($args[0] -eq 'login') {
    $output = & (Get-Command dotaws -CommandType Application) @args
    if ($LASTEXITCODE -eq 0 -and $output) {
      $output | Invoke-Expression
    }
    return
  }
  & (Get-Command dotaws -CommandType Application) @args
}
```

### Unchanged Commands

- `dotaws hook check` — no changes (already applies exports via eval in the existing hook)

### Exit Codes

No changes to exit codes.
