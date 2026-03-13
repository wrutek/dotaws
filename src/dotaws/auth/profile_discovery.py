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
        profiles.append(
            AwsProfileContext(
                name=name,
                source="config",
                region=settings.get("region"),
                role_arn=settings.get("role_arn"),
                source_profile=settings.get("source_profile"),
                mfa_serial=settings.get("mfa_serial"),
            )
        )
    return profiles


def find_profile(profile_name: str) -> AwsProfileContext | None:
    for profile in discover_profiles():
        if profile.name == profile_name:
            return profile
    return None
