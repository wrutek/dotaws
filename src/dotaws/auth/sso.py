"""AWS SSO (IAM Identity Center) authentication flow.

Implements the OIDC device authorization grant used by ``aws sso login``:
  1. Register an OIDC client (cached).
  2. Start device authorization → user opens browser to approve.
  3. Poll for the access token.
  4. Exchange access token for role credentials via the SSO service.
  5. Cache the access token for reuse until it expires.
"""

import hashlib
import json
import time
import webbrowser
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from dotaws.shared.errors import AuthError
from dotaws.shared.io import print_info, print_warning
from dotaws.shared.models import AwsProfileContext

_CLIENT_NAME = "dotaws"

# ---------------------------------------------------------------------------
# Token cache - compatible with the AWS CLI SSO cache layout
# (~/.aws/sso/cache/<sha1>.json)
# ---------------------------------------------------------------------------

def _cache_dir() -> Path:
    return Path.home() / ".aws" / "sso" / "cache"


def _cache_key(start_url: str, session_name: str | None = None) -> str:
    """Return the SHA-1 key that AWS CLI uses to index the SSO token cache."""
    source = session_name if session_name else start_url
    return hashlib.sha1(source.encode("utf-8")).hexdigest()  # noqa: S324


def _read_cached_token(start_url: str, session_name: str | None = None) -> dict[str, Any] | None:
    path = _cache_dir() / f"{_cache_key(start_url, session_name)}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    expires_at = data.get("expiresAt")
    if not expires_at:
        return None
    try:
        expiry = datetime.fromisoformat(expires_at)
    except ValueError:
        return None

    if expiry <= datetime.now(tz=UTC):
        return None
    return data


def _write_cached_token(
    start_url: str,
    session_name: str | None,
    token_data: dict[str, Any],
) -> None:
    cache = _cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / f"{_cache_key(start_url, session_name)}.json"
    path.write_text(json.dumps(token_data, default=str), encoding="utf-8")


# ---------------------------------------------------------------------------
# OIDC device authorization flow
# ---------------------------------------------------------------------------

def _register_client(oidc_client: Any) -> dict[str, Any]:
    """Register an OIDC client (short-lived, not cached)."""
    try:
        return oidc_client.register_client(
            clientName=_CLIENT_NAME,
            clientType="public",
        )
    except (ClientError, BotoCoreError) as exc:
        raise AuthError(
            "SSO client registration failed.",
            hint=str(exc),
        ) from exc


def _start_device_auth(
    oidc_client: Any,
    client_id: str,
    client_secret: str,
    start_url: str,
) -> dict[str, Any]:
    try:
        return oidc_client.start_device_authorization(
            clientId=client_id,
            clientSecret=client_secret,
            startUrl=start_url,
        )
    except (ClientError, BotoCoreError) as exc:
        raise AuthError(
            "SSO device authorization failed.",
            hint=str(exc),
        ) from exc


def _poll_for_token(
    oidc_client: Any,
    client_id: str,
    client_secret: str,
    device_code: str,
    interval: int = 5,
    expires_in: int = 600,
) -> dict[str, Any]:
    """Poll ``create_token`` until the user completes browser authorization."""
    deadline = time.monotonic() + expires_in
    while time.monotonic() < deadline:
        try:
            return oidc_client.create_token(
                clientId=client_id,
                clientSecret=client_secret,
                grantType="urn:ietf:params:oauth:grant-type:device_code",
                deviceCode=device_code,
            )
        except oidc_client.exceptions.AuthorizationPendingException:
            time.sleep(interval)
        except oidc_client.exceptions.SlowDownException:
            interval += 5
            time.sleep(interval)
        except (ClientError, BotoCoreError) as exc:
            raise AuthError(
                "SSO token retrieval failed.",
                hint=str(exc),
            ) from exc
    raise AuthError(
        "SSO authorization timed out.",
        hint="Re-run the command and complete the browser authorization.",
    )


def obtain_sso_token(
    start_url: str,
    sso_region: str,
    session_name: str | None = None,
) -> str:
    """Return a valid SSO access token, prompting via browser if needed."""
    cached = _read_cached_token(start_url, session_name)
    if cached is not None:
        print_info("Using cached SSO token.")
        return cached["accessToken"]

    oidc_client = boto3.client("sso-oidc", region_name=sso_region)

    registration = _register_client(oidc_client)
    client_id = registration["clientId"]
    client_secret = registration["clientSecret"]

    device_auth = _start_device_auth(oidc_client, client_id, client_secret, start_url)
    verification_uri = device_auth["verificationUriComplete"]
    user_code = device_auth["userCode"]
    interval = device_auth.get("interval", 5)
    expires_in = device_auth.get("expiresIn", 600)

    print_info("Opening browser for SSO authorization...")
    print_info(f"If the browser does not open, visit: {verification_uri}")
    print_info(f"Verification code: {user_code}")

    try:
        webbrowser.open(verification_uri)
    except Exception:  # pragma: no cover
        print_warning("Could not open browser automatically.")

    token_response = _poll_for_token(
        oidc_client,
        client_id,
        client_secret,
        device_auth["deviceCode"],
        interval=interval,
        expires_in=expires_in,
    )

    access_token: str = token_response["accessToken"]
    expires_at = datetime.now(tz=UTC).replace(microsecond=0) + timedelta(
        seconds=token_response.get("expiresIn", 28800),
    )

    _write_cached_token(start_url, session_name, {
        "startUrl": start_url,
        "region": sso_region,
        "accessToken": access_token,
        "expiresAt": expires_at.isoformat(),
    })

    return access_token


def get_sso_role_credentials(
    profile: AwsProfileContext,
    access_token: str,
) -> dict[str, Any]:
    """Exchange an SSO access token for temporary IAM role credentials."""
    if not profile.sso_account_id or not profile.sso_role_name:
        raise AuthError(
            "SSO profile is missing sso_account_id or sso_role_name.",
            hint="Check your AWS config for the SSO profile.",
        )
    sso_region = profile.sso_region or profile.region
    if not sso_region:
        raise AuthError(
            "SSO region could not be determined.",
            hint="Set sso_region in your AWS config profile.",
        )
    sso_client = boto3.client("sso", region_name=sso_region)
    try:
        response = sso_client.get_role_credentials(
            roleName=profile.sso_role_name,
            accountId=profile.sso_account_id,
            accessToken=access_token,
        )
    except (ClientError, BotoCoreError) as exc:
        raise AuthError(
            "Failed to retrieve SSO role credentials.",
            hint=str(exc),
        ) from exc
    return response["roleCredentials"]
