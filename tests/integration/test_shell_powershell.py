from dotaws.shell.powershell import render_env_exports


def test_powershell_export_syntax() -> None:
    output = render_env_exports({"AWS_PROFILE": "dev"})
    assert "$env:AWS_PROFILE" in output
