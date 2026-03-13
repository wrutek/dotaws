"""Bash rendering helpers."""


def render_env_exports(env: dict[str, str]) -> str:
    lines = [f"export {key}='{value}'" for key, value in env.items()]
    return "\n".join(lines)


def render_hook_snippet() -> str:
    return (
        "dotaws() {\n"
        "  if [ \"$1\" = \"login\" ]; then\n"
        "    case \" $* \" in\n"
        "      *\" --format json \"*|*\" --format=json \"*)\n"
        "        command dotaws \"$@\"\n"
        "        return\n"
        "        ;;\n"
        "    esac\n"
        "    local _dotaws_out _dotaws_rc\n"
        "    _dotaws_out=\"$(command dotaws \"$@\")\"\n"
        "    _dotaws_rc=$?\n"
        "    if [ \"$_dotaws_rc\" -eq 0 ] && [ -n \"$_dotaws_out\" ]; then\n"
        "      eval \"$_dotaws_out\"\n"
        "    fi\n"
        "    return \"$_dotaws_rc\"\n"
        "  fi\n"
        "  command dotaws \"$@\"\n"
        "}\n"
        "_dotaws_chpwd() {\n"
        "  if command -v dotaws >/dev/null 2>&1; then\n"
        "    eval \"$(command dotaws hook check --shell bash)\"\n"
        "  fi\n"
        "}\n"
        "PROMPT_COMMAND=\"_dotaws_chpwd${PROMPT_COMMAND:+;$PROMPT_COMMAND}\"\n"
    )
