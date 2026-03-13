"""Error types and exit code mapping."""

from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    USAGE = 2
    PROFILE = 3
    AUTH = 4
    CONFIG = 5
    SHELL = 6


class DotawsError(Exception):
    __slots__ = ("exit_code", "hint", "message")

    def __init__(self, message: str, exit_code: ExitCode, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.hint = hint

    def __str__(self) -> str:
        return self.message


class UsageError(DotawsError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message=message, exit_code=ExitCode.USAGE, hint=hint)


class ProfileResolutionError(DotawsError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message=message, exit_code=ExitCode.PROFILE, hint=hint)


class AuthError(DotawsError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message=message, exit_code=ExitCode.AUTH, hint=hint)


class ConfigError(DotawsError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message=message, exit_code=ExitCode.CONFIG, hint=hint)


class ShellOutputError(DotawsError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message=message, exit_code=ExitCode.SHELL, hint=hint)
