"""Input/output helpers."""

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console(stderr=True)


def print_error(message: str, hint: str | None = None) -> None:
    console.print(f"[red]Error:[/red] {message}")
    if hint:
        console.print(f"[yellow]Hint:[/yellow] {hint}")


def print_info(message: str) -> None:
    console.print(message)


def print_warning(message: str) -> None:
    console.print(f"[yellow]⚠ {message}[/yellow]")


def print_success(message: str) -> None:
    console.print(f"[green]✓ {message}[/green]")


def ask_text(message: str) -> str:
    return Prompt.ask(message, console=console)


def ask_confirm(message: str, default: bool = False) -> bool:
    return Confirm.ask(message, default=default, console=console)


def print_raw(text: str) -> None:
    """Write raw unformatted text to the console output stream."""
    f = console.file
    f.write(text)
    if not text.endswith("\n"):
        f.write("\n")
