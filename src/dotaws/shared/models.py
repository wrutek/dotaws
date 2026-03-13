"""Domain models for dotaws."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ShellType(StrEnum):
    POWERSHELL = "powershell"
    BASH = "bash"
    ZSH = "zsh"


class InvocationMode(StrEnum):
    INTERACTIVE = "interactive"
    NON_INTERACTIVE = "non_interactive"


@dataclass(slots=True)
class AwsProfileContext:
    name: str
    source: str = "merged"
    region: str | None = None
    role_arn: str | None = None
    source_profile: str | None = None
    mfa_serial: str | None = None
    sso_start_url: str | None = None
    sso_region: str | None = None
    sso_account_id: str | None = None
    sso_role_name: str | None = None
    sso_session: str | None = None

    @property
    def requires_mfa(self) -> bool:
        return bool(self.mfa_serial)

    @property
    def requires_sso(self) -> bool:
        return bool(self.sso_start_url or self.sso_session)


@dataclass(slots=True)
class AuthRequest:
    resolved_profile: str
    requested_profile: str | None = None
    invocation_mode: InvocationMode = InvocationMode.INTERACTIVE
    trigger: str = "manual_login"
    cwd: str | None = None


@dataclass(slots=True)
class AuthenticatedSession:
    profile_name: str
    access_key_id: str | None = None
    secret_access_key: str | None = None
    session_token: str | None = None
    expiration: datetime | None = None
    region: str | None = None

    @property
    def env_map(self) -> dict[str, str]:
        env: dict[str, str] = {"AWS_PROFILE": self.profile_name}
        if self.access_key_id:
            env["AWS_ACCESS_KEY_ID"] = self.access_key_id
        if self.secret_access_key:
            env["AWS_SECRET_ACCESS_KEY"] = self.secret_access_key
        if self.session_token:
            env["AWS_SESSION_TOKEN"] = self.session_token
        if self.region:
            env["AWS_REGION"] = self.region
        return env


@dataclass(slots=True)
class ShellExportPayload:
    shell: ShellType
    env: dict[str, str] = field(default_factory=dict)
    script: str = ""


@dataclass(slots=True)
class ProjectProfileMarker:
    file_path: str
    directory: str
    profile_name: str
    depth_from_cwd: int


@dataclass(slots=True)
class PromptSuppressionState:
    session_id: str
    directory_key: str
    suppressed_profile: str
    suppressed_at: datetime
