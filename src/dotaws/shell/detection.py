"""Shell detection utility."""

import os
import platform

from dotaws.shared.models import ShellType


def detect_shell(explicit: str | None = None) -> ShellType:
    if explicit:
        return ShellType(explicit.lower())

    shell_path = os.environ.get("SHELL", "").lower()
    if "zsh" in shell_path:
        return ShellType.ZSH
    if "bash" in shell_path:
        return ShellType.BASH

    if platform.system().lower() == "windows":
        return ShellType.POWERSHELL

    return ShellType.BASH
