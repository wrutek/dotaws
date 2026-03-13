from typer.testing import CliRunner

from dotaws.cli.app import app
from dotaws.shared.errors import AuthError
from dotaws.shared.models import AwsProfileContext


def test_mfa_failure_returns_exit_4(monkeypatch) -> None:
    runner = CliRunner()
    profile = AwsProfileContext(name="dev", mfa_serial="serial")
    monkeypatch.setattr("dotaws.auth.profile_discovery.find_profile", lambda _: profile)

    def fail(_profile, _token):
        raise AuthError("MFA authentication failed.", hint="Retry with valid token")

    monkeypatch.setattr("dotaws.auth.session_service.acquire_mfa_session", fail)

    result = runner.invoke(app, ["login", "--profile", "dev", "--mfa-code", "111111"])
    assert result.exit_code == 4
    assert "Retry with valid token" in result.stdout
