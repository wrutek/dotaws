"""Integration tests for SSO login flow with mocked AWS services."""

import json

from typer.testing import CliRunner

from dotaws.cli.app import app
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext


def _sso_profile(name: str = "sso-dev") -> AwsProfileContext:
    return AwsProfileContext(
        name=name,
        sso_start_url="https://example.awsapps.com/start",
        sso_region="us-east-1",
        sso_account_id="123456789012",
        sso_role_name="ReadOnly",
        region="us-west-2",
    )


def _stub_sso_auth(monkeypatch, profile: AwsProfileContext | None = None) -> None:
    """Patch profile discovery and SSO session acquisition."""
    prof = profile or _sso_profile()
    monkeypatch.setattr(
        "dotaws.auth.profile_discovery.find_profile",
        lambda name: AwsProfileContext(
            name=name,
            sso_start_url=prof.sso_start_url,
            sso_region=prof.sso_region,
            sso_account_id=prof.sso_account_id,
            sso_role_name=prof.sso_role_name,
            sso_session=prof.sso_session,
            region=prof.region,
        ),
    )
    monkeypatch.setattr(
        "dotaws.auth.session_service.acquire_sso_session",
        lambda p: AuthenticatedSession(
            profile_name=p.name,
            access_key_id="ASIAEXAMPLE",
            secret_access_key="SECRET_SSO",
            session_token="SSO_TOKEN",
            region=p.region,
        ),
    )


def test_sso_login_shell_output(monkeypatch) -> None:
    _stub_sso_auth(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(app, ["login", "--profile", "sso-dev", "--shell", "bash"])

    assert result.exit_code == 0
    assert "export AWS_PROFILE='sso-dev'" in result.stdout
    assert "export AWS_ACCESS_KEY_ID='ASIAEXAMPLE'" in result.stdout
    assert "export AWS_SESSION_TOKEN='SSO_TOKEN'" in result.stdout


def test_sso_login_powershell_output(monkeypatch) -> None:
    _stub_sso_auth(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "sso-dev", "--shell", "powershell"]
    )

    assert result.exit_code == 0
    assert '$env:AWS_PROFILE = "sso-dev"' in result.stdout
    assert '$env:AWS_ACCESS_KEY_ID = "ASIAEXAMPLE"' in result.stdout


def test_sso_login_json_output(monkeypatch) -> None:
    _stub_sso_auth(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "sso-dev", "--shell", "bash", "--format", "json"]
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["status"] == "ok"
    assert data["profile"] == "sso-dev"
    assert data["env"]["AWS_ACCESS_KEY_ID"] == "ASIAEXAMPLE"
    assert data["env"]["AWS_SESSION_TOKEN"] == "SSO_TOKEN"


def test_sso_login_non_interactive(monkeypatch) -> None:
    _stub_sso_auth(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["login", "--profile", "sso-dev", "--shell", "bash", "--non-interactive"],
    )

    assert result.exit_code == 0
    assert "export AWS_PROFILE='sso-dev'" in result.stdout


def test_sso_profile_skips_mfa_prompt(monkeypatch) -> None:
    """SSO profiles should not trigger MFA flow even if mfa_code is None."""
    _stub_sso_auth(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "sso-dev", "--shell", "bash"]
    )

    assert result.exit_code == 0
    # Should not contain any MFA prompt artifacts
    assert "MFA" not in result.stdout


def test_sso_login_with_sso_session(monkeypatch) -> None:
    """Profile using sso_session (named session) should also work."""
    prof = AwsProfileContext(
        name="sso-session-dev",
        sso_start_url="https://example.awsapps.com/start",
        sso_session="my-sso",
        sso_region="us-east-1",
        sso_account_id="123456789012",
        sso_role_name="Admin",
        region="eu-west-1",
    )
    _stub_sso_auth(monkeypatch, profile=prof)
    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "sso-session-dev", "--shell", "bash"]
    )

    assert result.exit_code == 0
    assert "export AWS_PROFILE='sso-session-dev'" in result.stdout


def test_sso_login_includes_region(monkeypatch) -> None:
    _stub_sso_auth(monkeypatch)
    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--profile", "sso-dev", "--shell", "bash"]
    )

    assert result.exit_code == 0
    assert "export AWS_REGION='us-west-2'" in result.stdout
