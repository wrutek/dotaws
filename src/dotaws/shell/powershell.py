"""PowerShell rendering helpers."""


def render_env_exports(env: dict[str, str]) -> str:
    lines = [f'$env:{key} = "{value}"' for key, value in env.items()]
    return "\n".join(lines)


def render_hook_snippet() -> str:
    return (
        "$_dotawsExe = (Get-Command dotaws -CommandType Application"
        " -ErrorAction SilentlyContinue).Source\n"
        "function dotaws {\n"
        "  if ($args.Count -gt 0 -and $args[0] -eq 'login') {\n"
        "    $fmt = 'shell'\n"
        "    for ($i = 0; $i -lt $args.Count; $i++) {\n"
        "      if ($args[$i] -eq '--format' -and ($i + 1) -lt $args.Count)"
        " { $fmt = $args[$i + 1] }\n"
        "      if ($args[$i] -match '^--format=(.+)$')"
        " { $fmt = $Matches[1] }\n"
        "    }\n"
        "    if ($fmt -eq 'json') {\n"
        "      & $_dotawsExe @args\n"
        "      return\n"
        "    }\n"
        "    $output = & $_dotawsExe @args | Out-String\n"
        "    if ($LASTEXITCODE -eq 0 -and $output.Trim()) {\n"
        "      Invoke-Expression $output\n"
        "    }\n"
        "    return\n"
        "  }\n"
        "  & $_dotawsExe @args\n"
        "}\n"
        "$function:DotawsPrompt = $function:prompt\n"
        "function prompt {\n"
        "  if ($_dotawsExe) {\n"
        "    & $_dotawsExe hook check --shell powershell | Invoke-Expression\n"
        "  }\n"
        "  if ($function:DotawsPrompt) { & $function:DotawsPrompt } else { 'PS> ' }\n"
        "}\n"
    )
