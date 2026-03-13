"""Login presentation helpers."""

import json

from dotaws.shared.models import ShellExportPayload


def to_shell(payload: ShellExportPayload) -> str:
    return payload.script


def to_json(payload: ShellExportPayload) -> str:
    return json.dumps(
        {
            "status": "ok",
            "shell": payload.shell.value,
            "env": payload.env,
        }
    )
