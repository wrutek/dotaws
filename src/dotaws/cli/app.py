"""CLI entrypoint."""

import typer

from dotaws.cli.commands import register_commands

app = typer.Typer(help="Cross-shell AWS helper CLI.")
register_commands(app)


def run() -> None:
    """Run CLI application."""
    app()


if __name__ == "__main__":
    run()
