from pathlib import Path

from typer.testing import CliRunner

from dotaws.cli.app import app


def test_auto_login_decline_sets_suppression(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    (tmp_path / ".aws_profile").write_text("dev", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("dotaws.cli.commands.hooks.ask_confirm", lambda *_args, **_kwargs: False)

    result = runner.invoke(app, ["hook", "check", "--shell", "bash"])
    assert result.exit_code == 0
    assert "DOTAWS_SUPPRESSION_STATE" in result.stdout
