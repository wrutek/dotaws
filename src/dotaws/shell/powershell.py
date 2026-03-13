"""PowerShell rendering helpers."""


def render_env_exports(env: dict[str, str]) -> str:
    lines = [f'$env:{key} = "{value}"' for key, value in env.items()]
    return "\n".join(lines)


def render_hook_snippet() -> str:
    return (
        "$function:DotawsPrompt = $function:prompt\n"
        "function prompt {\n"
        "  if (Get-Command dotaws -ErrorAction SilentlyContinue) {\n"
        "    dotaws hook check --shell powershell | Invoke-Expression\n"
        "  }\n"
        "  if ($function:DotawsPrompt) { & $function:DotawsPrompt } else { 'PS> ' }\n"
        "}\n"
    )
