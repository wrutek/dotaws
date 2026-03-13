"""CLI command registration."""

import typer

from dotaws.cli.commands import login as login_module
from dotaws.cli.commands.hooks import app as hooks_app


def register_commands(root: typer.Typer) -> None:
    root.command(name="login")(login_module.login)
    root.add_typer(hooks_app, name="hook")
