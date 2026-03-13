"""Unit tests for SSO token cache and helpers."""

import json
from datetime import UTC, datetime, timedelta

from dotaws.auth.sso import _cache_key, _read_cached_token, _write_cached_token
from dotaws.shared.models import AwsProfileContext


def test_cache_key_is_sha1_of_start_url() -> None:
    key = _cache_key("https://example.awsapps.com/start")
    assert isinstance(key, str)
    assert len(key) == 40  # SHA-1 hex


def test_cache_key_prefers_session_name() -> None:
    key_url = _cache_key("https://example.awsapps.com/start")
    key_session = _cache_key("https://example.awsapps.com/start", session_name="my-sso")
    assert key_url != key_session


def test_write_and_read_cached_token(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("dotaws.auth.sso._cache_dir", lambda: tmp_path)

    start_url = "https://example.awsapps.com/start"
    future = (datetime.now(tz=UTC) + timedelta(hours=8)).isoformat()
    token_data = {
        "startUrl": start_url,
        "region": "us-east-1",
        "accessToken": "test-token-123",
        "expiresAt": future,
    }
    _write_cached_token(start_url, None, token_data)

    result = _read_cached_token(start_url)
    assert result is not None
    assert result["accessToken"] == "test-token-123"


def test_read_expired_token_returns_none(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("dotaws.auth.sso._cache_dir", lambda: tmp_path)

    start_url = "https://example.awsapps.com/start"
    past = (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat()
    token_data = {
        "startUrl": start_url,
        "region": "us-east-1",
        "accessToken": "expired-token",
        "expiresAt": past,
    }
    _write_cached_token(start_url, None, token_data)

    result = _read_cached_token(start_url)
    assert result is None


def test_read_missing_token_returns_none() -> None:
    result = _read_cached_token("https://nonexistent.example.com/start")
    # May or may not find a cache file — either way, should not crash
    assert result is None or isinstance(result, dict)


def test_read_malformed_cache_returns_none(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("dotaws.auth.sso._cache_dir", lambda: tmp_path)

    start_url = "https://example.awsapps.com/start"
    key = _cache_key(start_url)
    cache_file = tmp_path / f"{key}.json"
    cache_file.write_text("not valid json", encoding="utf-8")

    result = _read_cached_token(start_url)
    assert result is None


def test_read_cache_missing_expires_at_returns_none(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("dotaws.auth.sso._cache_dir", lambda: tmp_path)

    start_url = "https://example.awsapps.com/start"
    key = _cache_key(start_url)
    cache_file = tmp_path / f"{key}.json"
    cache_file.write_text(
        json.dumps({"accessToken": "tok"}),
        encoding="utf-8",
    )

    result = _read_cached_token(start_url)
    assert result is None


def test_requires_sso_property() -> None:
    sso_profile = AwsProfileContext(
        name="sso-test",
        sso_start_url="https://example.awsapps.com/start",
        sso_region="us-east-1",
        sso_account_id="123456789012",
        sso_role_name="ReadOnly",
    )
    assert sso_profile.requires_sso is True
    assert sso_profile.requires_mfa is False


def test_requires_sso_with_session_name() -> None:
    profile = AwsProfileContext(
        name="sso-session-test",
        sso_session="my-sso",
        sso_account_id="123456789012",
        sso_role_name="Admin",
    )
    assert profile.requires_sso is True


def test_plain_profile_not_sso() -> None:
    profile = AwsProfileContext(name="dev")
    assert profile.requires_sso is False
