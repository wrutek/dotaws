from typer.testing import CliRunner

from dotaws.cli.app import app
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext


def test_interactive_login_selection(monkeypatch) -> None:
    runner = CliRunner()

    monkeypatch.setattr(
        "dotaws.auth.profile_discovery.discover_profiles",
        lambda: [AwsProfileContext(name="dev"), AwsProfileContext(name="prod")],
    )
    monkeypatch.setattr("dotaws.cli.commands.login.ask_text", lambda _: "1")
    monkeypatch.setattr(
        "dotaws.auth.session_service.acquire_session",
        lambda profile: AuthenticatedSession(
            profile_name=profile.name,
            access_key_id="AKIA",
            secret_access_key="S",
        ),
    )

    result = runner.invoke(app, ["login", "--shell", "bash"])
    assert result.exit_code == 0
    assert "AWS_PROFILE" in result.stdout
