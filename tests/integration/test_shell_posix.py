from dotaws.shell.bash import render_env_exports as render_bash
from dotaws.shell.zsh import render_env_exports as render_zsh


def test_bash_export_syntax() -> None:
    output = render_bash({"AWS_PROFILE": "dev"})
    assert "export AWS_PROFILE='dev'" in output


def test_zsh_export_syntax() -> None:
    output = render_zsh({"AWS_PROFILE": "dev"})
    assert "export AWS_PROFILE='dev'" in output
