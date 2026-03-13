from typer.testing import CliRunner

from dotaws.cli.app import app


def test_login_non_interactive_requires_profile() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["login", "--non-interactive"])
    assert result.exit_code == 2
    assert "Profile input required" in result.stdout


def test_login_json_contract(monkeypatch) -> None:
    runner = CliRunner()

    def fake_execute_login(**_: object) -> str:
        return '{"status":"ok","profile":"dev","shell":"bash","env":{"AWS_PROFILE":"dev"}}'

    monkeypatch.setattr("dotaws.cli.commands.login.execute_login", fake_execute_login)
    result = runner.invoke(app, ["login", "--profile", "dev", "--format", "json"])
    assert result.exit_code == 0
    assert '"status":"ok"' in result.stdout
