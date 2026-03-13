from typer.testing import CliRunner

from dotaws.cli.app import app


def test_hook_print_requires_shell() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["hook", "print"])
    assert result.exit_code != 0


def test_hook_print_bash() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["hook", "print", "--shell", "bash"])
    assert result.exit_code == 0
    assert "PROMPT_COMMAND" in result.stdout
