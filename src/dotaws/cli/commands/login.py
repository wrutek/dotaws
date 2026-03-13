"""Login command implementation."""

import json
import os
import sys

import typer

from dotaws.auth import profile_discovery, session_service
from dotaws.auth.credential_export import build_export_payload
from dotaws.auth.mfa import get_mfa_token
from dotaws.project.profile_marker import find_nearest_marker
from dotaws.shared.errors import DotawsError, ProfileResolutionError, UsageError
from dotaws.shared.io import (
    ask_confirm,
    ask_text,
    print_error,
    print_info,
    print_raw,
    print_success,
    print_warning,
)
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext, InvocationMode
from dotaws.shell.detection import detect_shell


def _pick_profile_interactive(profiles: list[AwsProfileContext]) -> AwsProfileContext:
    print_info("Select AWS profile:")
    for idx, profile in enumerate(profiles, start=1):
        print_info(f"{idx}. {profile.name}")
    answer = ask_text("Enter number")
    try:
        choice = int(answer)
        return profiles[choice - 1]
    except (ValueError, IndexError) as exc:  # pragma: no cover - user input parsing
        raise UsageError(
            "Invalid profile selection.",
            hint="Enter a valid number from list.",
        ) from exc


def _resolve_profile(profile_name: str | None, mode: InvocationMode) -> AwsProfileContext:
    if mode is InvocationMode.NON_INTERACTIVE and not profile_name:
        raise UsageError(
            "Profile input required in non-interactive mode.",
            hint="Provide --profile <name>.",
        )

    if profile_name:
        resolved = profile_discovery.find_profile(profile_name)
        if resolved is None:
            raise ProfileResolutionError(
                f"Profile '{profile_name}' not found.",
                hint="Run login without --profile to list options.",
            )
        return resolved

    marker = find_nearest_marker()
    if marker is not None:
        resolved = profile_discovery.find_profile(marker.profile_name)
        if resolved is None:
            raise ProfileResolutionError(
                f"Profile '{marker.profile_name}' from .aws_profile not found.",
                hint="Update .aws_profile or configure matching AWS profile.",
            )
        return resolved

    profiles = profile_discovery.discover_profiles()
    if not profiles:
        raise ProfileResolutionError("No AWS profiles found.")
    return _pick_profile_interactive(profiles)


def _authenticate(
    profile: AwsProfileContext,
    mfa_code: str | None,
    mode: InvocationMode,
) -> AuthenticatedSession:
    if profile.requires_mfa:
        if mode is InvocationMode.NON_INTERACTIVE and not mfa_code:
            raise UsageError(
                "MFA token required in non-interactive mode.",
                hint="Provide --mfa-code <token>.",
            )
        token = get_mfa_token(mfa_code)
        return session_service.acquire_mfa_session(profile, token)
    return session_service.acquire_session(profile)


def execute_login(
    *,
    profile_name: str | None,
    mfa_code: str | None,
    shell: str | None,
    non_interactive: bool,
    output_format: str,
) -> str:
    mode = InvocationMode.NON_INTERACTIVE if non_interactive else InvocationMode.INTERACTIVE
    profile = _resolve_profile(profile_name, mode)
    session = _authenticate(profile, mfa_code, mode)
    payload = build_export_payload(session, detect_shell(shell))

    if output_format == "json":
        return json.dumps(
            {
                "status": "ok",
                "profile": profile.name,
                "shell": payload.shell.value,
                "env": payload.env,
            }
        )
    return payload.script


def _check_existing_env_vars(env: dict[str, str]) -> list[str]:
    """Return names of env vars from *env* that already exist in os.environ."""
    return [key for key in env if key in os.environ]


def _should_prompt_export(*, non_interactive: bool, output_format: str) -> bool:
    """Return True when the interactive export prompt should be shown."""
    if non_interactive:
        return False
    if output_format == "json":
        return False
    return sys.stdout.isatty()


def login(
    profile: str | None = typer.Option(default=None, help="Explicit profile name."),
    mfa_code: str | None = typer.Option(default=None, help="MFA token code."),
    shell: str | None = typer.Option(default=None, help="Target shell output."),
    non_interactive: bool = typer.Option(default=False, help="Disable prompts."),
    format: str = typer.Option(default="shell", help="Output format: shell|json."),
) -> None:
    """Authenticate and export shell credentials."""
    try:
        mode = InvocationMode.NON_INTERACTIVE if non_interactive else InvocationMode.INTERACTIVE
        resolved = _resolve_profile(profile, mode)
        session = _authenticate(resolved, mfa_code, mode)
        payload = build_export_payload(session, detect_shell(shell))

        if format == "json":
            print(json.dumps({
                "status": "ok",
                "profile": resolved.name,
                "shell": payload.shell.value,
                "env": payload.env,
            }))
            return

        script = payload.script

        if not _should_prompt_export(non_interactive=non_interactive, output_format=format):
            print(script)
            return

        if ask_confirm("Export credentials to current shell?", default=True):
            existing = _check_existing_env_vars(payload.env)
            if existing:
                print_warning(f"Overwriting: {', '.join(existing)}")
            print(script)
            print_success(
                f"Exported {len(payload.env)} variables for profile '{resolved.name}'"
            )
        else:
            print_raw(script)
    except DotawsError as exc:
        print_error(exc.message, exc.hint)
        raise typer.Exit(code=int(exc.exit_code)) from exc
    except Exception as exc:  # pragma: no cover
        print_error("Unexpected error.", str(exc))
        raise typer.Exit(code=1) from exc
