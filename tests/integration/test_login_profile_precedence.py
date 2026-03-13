from pathlib import Path

from typer.testing import CliRunner

from dotaws.cli.app import app
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext


def test_explicit_profile_overrides_marker(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    marker = tmp_path / ".aws_profile"
    marker.write_text("marker-profile", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "dotaws.auth.profile_discovery.find_profile",
        lambda name: AwsProfileContext(name=name),
    )
    monkeypatch.setattr(
        "dotaws.auth.session_service.acquire_session",
        lambda profile: AuthenticatedSession(profile_name=profile.name),
    )

    result = runner.invoke(app, ["login", "--profile", "explicit", "--shell", "bash"])
    assert result.exit_code == 0
    assert "AWS_PROFILE='explicit'" in result.stdout
