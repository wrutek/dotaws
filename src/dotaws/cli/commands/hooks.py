"""Hook command implementation."""

import os

import typer

from dotaws.cli.commands.login import execute_login
from dotaws.project.profile_marker import find_nearest_marker
from dotaws.project.prompt_state import (
    encode_state,
    is_suppressed,
    parse_state,
    record_decline,
)
from dotaws.shared.errors import DotawsError, ShellOutputError
from dotaws.shared.io import ask_confirm, print_error
from dotaws.shell import bash, powershell, zsh

app = typer.Typer(help="Shell hook helpers.")


@app.command("print")
def hook_print(shell: str = typer.Option(..., help="powershell|bash|zsh")) -> None:
    try:
        rendered = _render_hook(shell)
        print(rendered)
    except DotawsError as exc:
        print_error(exc.message, exc.hint)
        raise typer.Exit(code=int(exc.exit_code)) from exc


@app.command("check")
def hook_check(shell: str = typer.Option(..., help="powershell|bash|zsh")) -> None:
    marker = find_nearest_marker()
    if marker is None:
        return

    session_id = os.environ.get("DOTAWS_SESSION_ID", "default")
    state_raw = os.environ.get("DOTAWS_SUPPRESSION_STATE")
    state = parse_state(state_raw)

    if is_suppressed(
        state,
        session_id=session_id,
        directory_key=marker.directory,
        profile_name=marker.profile_name,
    ):
        return

    if not ask_confirm(
        f"Use AWS profile '{marker.profile_name}' for this directory?",
        default=False,
    ):
        record_decline(
            state,
            session_id=session_id,
            directory_key=marker.directory,
            profile_name=marker.profile_name,
        )
        encoded = encode_state(state)
        env_command = _render_suppression_export(shell, encoded)
        print(env_command)
        return

    output = execute_login(
        profile_name=marker.profile_name,
        mfa_code=None,
        shell=shell,
        non_interactive=False,
        output_format="shell",
    )
    print(output)


def _render_hook(shell: str) -> str:
    normalized = shell.lower()
    if normalized == "powershell":
        return powershell.render_hook_snippet()
    if normalized == "bash":
        return bash.render_hook_snippet()
    if normalized == "zsh":
        return zsh.render_hook_snippet()
    raise ShellOutputError("Unsupported shell for hook rendering.")


def _render_suppression_export(shell: str, encoded: str) -> str:
    normalized = shell.lower()
    if normalized == "powershell":
        return f'$env:DOTAWS_SUPPRESSION_STATE = "{encoded}"'
    if normalized in {"bash", "zsh"}:
        return f"export DOTAWS_SUPPRESSION_STATE='{encoded}'"
    raise ShellOutputError("Unsupported shell for suppression export.")
