import pytest

from dotaws.auth.mfa import get_mfa_token
from dotaws.shared.errors import AuthError


def test_get_mfa_token_prefers_initial() -> None:
    assert get_mfa_token("123456") == "123456"


def test_get_mfa_token_rejects_empty(monkeypatch) -> None:
    monkeypatch.setattr("dotaws.auth.mfa.ask_text", lambda _: "")
    with pytest.raises(AuthError):
        get_mfa_token()
