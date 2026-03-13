"""Bash rendering helpers."""


def render_env_exports(env: dict[str, str]) -> str:
    lines = [f"export {key}='{value}'" for key, value in env.items()]
    return "\n".join(lines)


def render_hook_snippet() -> str:
    return (
        "_dotaws_chpwd() {\n"
        "  if command -v dotaws >/dev/null 2>&1; then\n"
        "    eval \"$(dotaws hook check --shell bash)\"\n"
        "  fi\n"
        "}\n"
        "PROMPT_COMMAND=\"_dotaws_chpwd${PROMPT_COMMAND:+;$PROMPT_COMMAND}\"\n"
    )
