from typer.testing import CliRunner

from dotaws.cli.app import app


def test_login_non_interactive_requires_profile() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["login", "--non-interactive"])
    assert result.exit_code == 2
    assert "Profile input required" in result.stdout


def test_login_json_contract(monkeypatch) -> None:
    runner = CliRunner()

    monkeypatch.setattr(
        "dotaws.auth.profile_discovery.find_profile",
        lambda name: type("P", (), {"name": name, "requires_mfa": False, "requires_sso": False})(),
    )
    monkeypatch.setattr(
        "dotaws.auth.session_service.acquire_session",
        lambda profile: type(
            "S",
            (),
            {
                "profile_name": profile.name,
                "access_key_id": "AK",
                "secret_access_key": "SK",
                "session_token": None,
                "region": None,
                "env_map": {
                    "AWS_PROFILE": profile.name,
                    "AWS_ACCESS_KEY_ID": "AK",
                    "AWS_SECRET_ACCESS_KEY": "SK",
                },
            },
        )(),
    )

    result = runner.invoke(app, ["login", "--profile", "dev", "--format", "json"])
    assert result.exit_code == 0
    assert '"status"' in result.stdout
