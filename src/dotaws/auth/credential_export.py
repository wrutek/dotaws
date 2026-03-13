"""Credential export orchestration."""

from dotaws.shared.errors import ShellOutputError
from dotaws.shared.models import AuthenticatedSession, ShellExportPayload, ShellType
from dotaws.shell import bash, powershell, zsh


def build_export_payload(session: AuthenticatedSession, shell: ShellType) -> ShellExportPayload:
    env = session.env_map
    if shell is ShellType.POWERSHELL:
        script = powershell.render_env_exports(env)
    elif shell is ShellType.BASH:
        script = bash.render_env_exports(env)
    elif shell is ShellType.ZSH:
        script = zsh.render_env_exports(env)
    else:
        raise ShellOutputError(message=f"Unsupported shell: {shell}")
    return ShellExportPayload(shell=shell, env=env, script=script)
