"""Prompt suppression state helpers for shell session."""

import json
from datetime import UTC, datetime

from dotaws.shared.models import PromptSuppressionState


def parse_state(raw: str | None) -> dict[str, PromptSuppressionState]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    state: dict[str, PromptSuppressionState] = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        try:
            state[key] = PromptSuppressionState(
                session_id=str(value.get("session_id", "")),
                directory_key=key,
                suppressed_profile=str(value.get("suppressed_profile", "")),
                suppressed_at=datetime.fromisoformat(str(value.get("suppressed_at"))),
            )
        except (KeyError, ValueError, TypeError):
            continue
    return state


def encode_state(state: dict[str, PromptSuppressionState]) -> str:
    serializable = {
        key: {
            "session_id": value.session_id,
            "suppressed_profile": value.suppressed_profile,
            "suppressed_at": value.suppressed_at.isoformat(),
        }
        for key, value in state.items()
    }
    return json.dumps(serializable)


def record_decline(
    state: dict[str, PromptSuppressionState],
    *,
    session_id: str,
    directory_key: str,
    profile_name: str,
) -> dict[str, PromptSuppressionState]:
    state[directory_key] = PromptSuppressionState(
        session_id=session_id,
        directory_key=directory_key,
        suppressed_profile=profile_name,
        suppressed_at=datetime.now(UTC),
    )
    return state


def is_suppressed(
    state: dict[str, PromptSuppressionState],
    *,
    session_id: str,
    directory_key: str,
    profile_name: str,
) -> bool:
    item = state.get(directory_key)
    if item is None:
        return False
    return item.session_id == session_id and item.suppressed_profile == profile_name
