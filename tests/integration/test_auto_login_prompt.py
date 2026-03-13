from pathlib import Path

from typer.testing import CliRunner

from dotaws.cli.app import app


def test_auto_login_prompt_accept(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    (tmp_path / ".aws_profile").write_text("dev", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("dotaws.cli.commands.hooks.ask_confirm", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        "dotaws.cli.commands.hooks.execute_login",
        lambda **_kwargs: "export AWS_PROFILE='dev'",
    )

    result = runner.invoke(app, ["hook", "check", "--shell", "bash"])
    assert result.exit_code == 0
    assert "AWS_PROFILE" in result.stdout
