"""MFA challenge handling."""

from dotaws.shared.errors import AuthError
from dotaws.shared.io import ask_text


def get_mfa_token(initial_code: str | None = None) -> str:
    if initial_code:
        return initial_code
    token = ask_text("Enter MFA token")
    if not token.strip():
        raise AuthError(
            "MFA token is required.",
            hint="Provide --mfa-code or enter token interactively.",
        )
    return token.strip()
