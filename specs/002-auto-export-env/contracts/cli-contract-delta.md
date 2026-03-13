# CLI Contract Delta: Auto-Export Environment Variables

**Feature**: 002-auto-export-env  
**Date**: 2026-03-13

## Changed Command: `dotaws login`

### Before (current behavior)

```
$ dotaws login --profile myprofile
export AWS_PROFILE='myprofile'
export AWS_ACCESS_KEY_ID='ASIA...'
export AWS_SECRET_ACCESS_KEY='...'
export AWS_SESSION_TOKEN='...'
```

Always prints export statements to stdout. User must copy-paste or wrap in `eval`.

### After (new behavior)

#### Interactive + TTY + shell format:

```
$ dotaws login --profile myprofile
Export credentials to current shell? [Y/n]: y
⚠ Overwriting: AWS_PROFILE, AWS_ACCESS_KEY_ID    # only if vars already exist
✓ Exported 4 variables for profile 'myprofile'
```

Variables are set via eval-ready output (same mechanism as hooks).

If user declines:

```
$ dotaws login --profile myprofile
Export credentials to current shell? [Y/n]: n
export AWS_PROFILE='myprofile'
export AWS_ACCESS_KEY_ID='ASIA...'
export AWS_SECRET_ACCESS_KEY='...'
export AWS_SESSION_TOKEN='...'
```

Falls back to printing export statements (current behavior).

#### Non-interactive / JSON / piped: Unchanged

```
$ dotaws login --profile myprofile --non-interactive
export AWS_PROFILE='myprofile'
...

$ dotaws login --profile myprofile --format json
{"status": "ok", "profile": "myprofile", ...}

$ dotaws login --profile myprofile | grep AWS
export AWS_PROFILE='myprofile'
...
```

### Unchanged Commands

- `dotaws hook print` — no changes
- `dotaws hook check` — no changes (already applies exports via eval)

### Exit Codes

No changes to exit codes.
