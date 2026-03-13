from typer.testing import CliRunner

from dotaws.cli.app import app


def test_non_interactive_missing_input_fails_fast() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["login", "--non-interactive", "--shell", "bash"])
    assert result.exit_code == 2
    assert "Provide --profile" in result.stdout
