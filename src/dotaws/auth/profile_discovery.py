"""AWS profile discovery."""

from botocore.exceptions import BotoCoreError
from botocore.session import Session as BotocoreSession

from dotaws.shared.errors import ConfigError
from dotaws.shared.models import AwsProfileContext


def discover_profiles() -> list[AwsProfileContext]:
    """Discover AWS profiles from shared AWS config and credentials."""
    try:
        session = BotocoreSession()
        config = session.full_config
    except BotoCoreError as exc:  # pragma: no cover - botocore-dependent
        raise ConfigError("Unable to load AWS configuration.", hint=str(exc)) from exc

    profiles_section = config.get("profiles", {})
    if not isinstance(profiles_section, dict):
        raise ConfigError("Malformed AWS profile configuration.")

    profiles: list[AwsProfileContext] = []
    for name, settings in sorted(profiles_section.items()):
        if not isinstance(settings, dict):
            continue

        # Resolve sso_session indirection: if profile references an
        # [sso-session X] block, pull sso_start_url / sso_region from it.
        sso_session_name = settings.get("sso_session")
        sso_start_url = settings.get("sso_start_url")
        sso_region = settings.get("sso_region")
        if sso_session_name:
            sso_sessions = config.get("sso_sessions", {})
            sso_block = sso_sessions.get(sso_session_name, {})
            if not sso_start_url:
                sso_start_url = sso_block.get("sso_start_url")
            if not sso_region:
                sso_region = sso_block.get("sso_region")

        profiles.append(
            AwsProfileContext(
                name=name,
                source="config",
                region=settings.get("region"),
                role_arn=settings.get("role_arn"),
                source_profile=settings.get("source_profile"),
                mfa_serial=settings.get("mfa_serial"),
                sso_start_url=sso_start_url,
                sso_region=sso_region,
                sso_account_id=settings.get("sso_account_id"),
                sso_role_name=settings.get("sso_role_name"),
                sso_session=sso_session_name,
            )
        )
    return profiles


def find_profile(profile_name: str) -> AwsProfileContext | None:
    for profile in discover_profiles():
        if profile.name == profile_name:
            return profile
    return None
