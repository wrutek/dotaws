"""Tests for auto-export environment variables feature."""

import json
from unittest.mock import patch

from typer.testing import CliRunner

from dotaws.cli.app import app
from dotaws.cli.commands.login import _check_existing_env_vars, _should_prompt_export
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext


def _stub_auth(monkeypatch: object, profile_name: str = "dev") -> None:
    """Patch profile discovery and session acquisition for tests."""
    mp: object = monkeypatch
    mp.setattr(  # type: ignore[union-attr]
        "dotaws.auth.profile_discovery.find_profile",
        lambda name: AwsProfileContext(name=name),
    )
    mp.setattr(  # type: ignore[union-attr]
        "dotaws.auth.session_service.acquire_session",
        lambda profile: AuthenticatedSession(
            profile_name=profile.name,
            access_key_id="AKIATEST",
            secret_access_key="SECRET",
            session_token="TOKEN",
        ),
    )


# ---------------------------------------------------------------------------
# T003: User confirms export → eval-ready script + success message
# ---------------------------------------------------------------------------

def test_confirm_export_prints_script_and_success(monkeypatch) -> None:
    _stub_auth(monkeypatch)
    monkeypatch.setattr("dotaws.cli.commands.login.ask_confirm", lambda *_a, **_kw: True)
    monkeypatch.setattr("dotaws.cli.commands.login._should_prompt_export", lambda **_kw: True)

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "dev", "--shell", "bash"])

    assert result.exit_code == 0
    assert "export AWS_PROFILE=" in result.stdout
    assert "Exported" in result.stdout
    assert "dev" in result.stdout


# ---------------------------------------------------------------------------
# T004: User declines export → raw export statements (current behavior)
# ---------------------------------------------------------------------------

def test_decline_export_prints_raw_script(monkeypatch) -> None:
    _stub_auth(monkeypatch)
    monkeypatch.setattr("dotaws.cli.commands.login.ask_confirm", lambda *_a, **_kw: False)
    monkeypatch.setattr("dotaws.cli.commands.login._should_prompt_export", lambda **_kw: True)

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "dev", "--shell", "bash"])

    assert result.exit_code == 0
    assert "export AWS_PROFILE=" in result.stdout
    # Should NOT have success message
    assert "Exported" not in result.stdout


# ---------------------------------------------------------------------------
# T005: Existing AWS env vars → overwrite warning
# ---------------------------------------------------------------------------

def test_overwrite_warning_shown_when_vars_exist(monkeypatch) -> None:
    _stub_auth(monkeypatch)
    monkeypatch.setattr("dotaws.cli.commands.login.ask_confirm", lambda *_a, **_kw: True)
    monkeypatch.setattr("dotaws.cli.commands.login._should_prompt_export", lambda **_kw: True)
    monkeypatch.setenv("AWS_PROFILE", "old-profile")

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "dev", "--shell", "bash"])

    assert result.exit_code == 0
    assert "Overwriting" in result.stdout
    assert "AWS_PROFILE" in result.stdout
    assert "Exported" in result.stdout


# ---------------------------------------------------------------------------
# T007: Shell-specific output verification
# ---------------------------------------------------------------------------

def test_bash_export_syntax(monkeypatch) -> None:
    _stub_auth(monkeypatch)
    monkeypatch.setattr("dotaws.cli.commands.login.ask_confirm", lambda *_a, **_kw: True)
    monkeypatch.setattr("dotaws.cli.commands.login._should_prompt_export", lambda **_kw: True)

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "dev", "--shell", "bash"])
    assert "export AWS_PROFILE='dev'" in result.stdout


def test_powershell_export_syntax(monkeypatch) -> None:
    _stub_auth(monkeypatch)
    monkeypatch.setattr("dotaws.cli.commands.login.ask_confirm", lambda *_a, **_kw: True)
    monkeypatch.setattr("dotaws.cli.commands.login._should_prompt_export", lambda **_kw: True)

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "dev", "--shell", "powershell"])
    assert '$env:AWS_PROFILE = "dev"' in result.stdout


def test_zsh_export_syntax(monkeypatch) -> None:
    _stub_auth(monkeypatch)
    monkeypatch.setattr("dotaws.cli.commands.login.ask_confirm", lambda *_a, **_kw: True)
    monkeypatch.setattr("dotaws.cli.commands.login._should_prompt_export", lambda **_kw: True)

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "dev", "--shell", "zsh"])
    assert "export AWS_PROFILE='dev'" in result.stdout


# ---------------------------------------------------------------------------
# T008: Non-interactive mode skips prompt
# ---------------------------------------------------------------------------

def test_non_interactive_skips_prompt(monkeypatch) -> None:
    _stub_auth(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "dev", "--shell", "bash", "--non-interactive"]
    )

    assert result.exit_code == 0
    assert "export AWS_PROFILE=" in result.stdout
    # No success message — prompt was not shown
    assert "Exported" not in result.stdout


# ---------------------------------------------------------------------------
# T010: JSON format skips prompt, outputs JSON unchanged
# ---------------------------------------------------------------------------

def test_json_format_skips_prompt(monkeypatch) -> None:
    _stub_auth(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "dev", "--shell", "bash", "--format", "json"]
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"
    assert data["profile"] == "dev"
    assert "AWS_PROFILE" in data["env"]
    # No export prompt or success message
    assert "Exported" not in result.stdout


# ---------------------------------------------------------------------------
# T012: Non-TTY stdout skips prompt
# ---------------------------------------------------------------------------

def test_non_tty_skips_prompt() -> None:
    """_should_prompt_export returns False when stdout is not a TTY."""
    with patch("dotaws.cli.commands.login.sys") as mock_sys:
        mock_sys.stdout.isatty.return_value = False
        assert _should_prompt_export(non_interactive=False, output_format="shell") is False


def test_tty_enables_prompt() -> None:
    """_should_prompt_export returns True when stdout is a TTY and interactive."""
    with patch("dotaws.cli.commands.login.sys") as mock_sys:
        mock_sys.stdout.isatty.return_value = True
        assert _should_prompt_export(non_interactive=False, output_format="shell") is True


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_check_existing_env_vars_detects_set_vars(monkeypatch) -> None:
    monkeypatch.setenv("AWS_PROFILE", "old")
    result = _check_existing_env_vars({"AWS_PROFILE": "new", "AWS_ACCESS_KEY_ID": "AK"})
    assert result == ["AWS_PROFILE"]


def test_check_existing_env_vars_returns_empty_when_none_set() -> None:
    result = _check_existing_env_vars({"SOME_NEW_VAR": "val"})
    assert result == []


def test_should_prompt_export_false_for_non_interactive() -> None:
    assert _should_prompt_export(non_interactive=True, output_format="shell") is False


def test_should_prompt_export_false_for_json() -> None:
    assert _should_prompt_export(non_interactive=False, output_format="json") is False
