"""Session acquisition services."""

from datetime import UTC, datetime

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from dotaws.auth.sso import get_sso_role_credentials, obtain_sso_token
from dotaws.shared.errors import AuthError, ProfileResolutionError
from dotaws.shared.models import AuthenticatedSession, AwsProfileContext


def _base_session(profile_name: str) -> boto3.Session:
    try:
        return boto3.Session(profile_name=profile_name)
    except (BotoCoreError, ClientError) as exc:  # pragma: no cover - boto3 dependent
        raise ProfileResolutionError(
            f"Profile '{profile_name}' could not be loaded.",
            hint="Check your AWS profile configuration.",
        ) from exc


def acquire_session(profile: AwsProfileContext) -> AuthenticatedSession:
    """Acquire non-MFA session based on selected profile."""
    session = _base_session(profile.name)
    creds = session.get_credentials()
    if creds is None:
        raise AuthError("No credentials available for selected profile.")
    frozen = creds.get_frozen_credentials()
    return AuthenticatedSession(
        profile_name=profile.name,
        access_key_id=frozen.access_key,
        secret_access_key=frozen.secret_key,
        session_token=frozen.token,
        region=session.region_name or profile.region,
    )


def acquire_mfa_session(profile: AwsProfileContext, token_code: str) -> AuthenticatedSession:
    """Acquire session credentials with MFA via STS GetSessionToken."""
    if not profile.mfa_serial:
        raise AuthError("Profile does not define MFA serial.")

    session = _base_session(profile.name)
    sts = session.client("sts")
    try:
        response = sts.get_session_token(SerialNumber=profile.mfa_serial, TokenCode=token_code)
    except (ClientError, BotoCoreError) as exc:
        raise AuthError("MFA authentication failed.", hint=str(exc)) from exc

    credentials = response["Credentials"]
    expiration_raw = credentials.get("Expiration")
    expiration: datetime | None = None
    if isinstance(expiration_raw, datetime):
        expiration = expiration_raw
    return AuthenticatedSession(
        profile_name=profile.name,
        access_key_id=credentials.get("AccessKeyId"),
        secret_access_key=credentials.get("SecretAccessKey"),
        session_token=credentials.get("SessionToken"),
        expiration=expiration,
        region=session.region_name or profile.region,
    )


def acquire_sso_session(profile: AwsProfileContext) -> AuthenticatedSession:
    """Acquire session credentials via AWS SSO (IAM Identity Center).

    Runs the OIDC device authorization flow if the cached SSO token is
    missing or expired, then exchanges the access token for temporary
    IAM role credentials.
    """
    if not profile.sso_start_url:
        raise AuthError(
            "SSO profile is missing sso_start_url.",
            hint="Check your AWS config for the SSO profile.",
        )
    sso_region = profile.sso_region or profile.region
    if not sso_region:
        raise AuthError(
            "SSO region could not be determined.",
            hint="Set sso_region in your AWS config profile.",
        )

    access_token = obtain_sso_token(
        start_url=profile.sso_start_url,
        sso_region=sso_region,
        session_name=profile.sso_session,
    )

    role_creds = get_sso_role_credentials(profile, access_token)

    expiration_ms = role_creds.get("expiration")
    expiration: datetime | None = None
    if expiration_ms is not None:
        expiration = datetime.fromtimestamp(expiration_ms / 1000, tz=UTC)

    return AuthenticatedSession(
        profile_name=profile.name,
        access_key_id=role_creds.get("accessKeyId"),
        secret_access_key=role_creds.get("secretAccessKey"),
        session_token=role_creds.get("sessionToken"),
        expiration=expiration,
        region=profile.region,
    )
