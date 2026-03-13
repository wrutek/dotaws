"""Shared test fixtures."""

import pytest
from rich.console import Console

import dotaws.shared.io as io_module


@pytest.fixture(autouse=True)
def _redirect_console_to_stdout():
    """Swap the Rich console to stdout so CliRunner can capture all output.

    In production ``Console(stderr=True)`` keeps UX messages on stderr so the
    shell wrapper only captures export scripts from stdout.  Click/Typer's
    ``CliRunner`` does **not** intercept ``sys.stderr``, so tests would miss
    those messages.  This fixture temporarily replaces the module-level console
    with a stdout-based one for the duration of each test.
    """
    original = io_module.console
    io_module.console = Console()
    yield
    io_module.console = original
