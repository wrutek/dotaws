from typer.testing import CliRunner

from dotaws.cli.app import app
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext


def test_mfa_success(monkeypatch) -> None:
    runner = CliRunner()
    profile = AwsProfileContext(name="dev", mfa_serial="arn:aws:iam::123:mfa/user")
    monkeypatch.setattr("dotaws.auth.profile_discovery.find_profile", lambda _: profile)
    monkeypatch.setattr(
        "dotaws.auth.session_service.acquire_mfa_session",
        lambda _p, _t: AuthenticatedSession(profile_name="dev", session_token="TOKEN"),
    )

    result = runner.invoke(
        app,
        ["login", "--profile", "dev", "--mfa-code", "123456", "--shell", "bash"],
    )
    assert result.exit_code == 0
    assert "AWS_SESSION_TOKEN" in result.stdout
