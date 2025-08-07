"""A console utility for rich text output in CLI applications, with verbosity control and styled messages."""

import rich.console


class Console:
    def __init__(self, verbosity: int = 0):
        self.verbosity = verbosity
        self.console = rich.console.Console()

    def info(self, msg, **kwargs):
        """Print a message only if verbosity is 1 or more."""
        if self.verbosity >= 1:
            self.console.print(msg, **kwargs)

    def debug(self, msg, **kwargs):
        """Print a message only if verbosity is 2 or more."""
        if self.verbosity >= 2:
            self.console.print("[dim]DEBUG:[/]", msg, **kwargs, style="grey70")

    def error(self, msg, **kwargs):
        """Print an error message."""
        self.console.print("[bold red]ERROR:[/]", msg, **kwargs)

    def warning(self, msg, **kwargs):
        """Print a warning message."""
        self.console.print("[bold yellow]WARNING:[/]", msg, **kwargs)

    def success(self, msg, **kwargs):
        """Print a success message."""
        self.console.print("[bold green]SUCCESS:[/]", msg, **kwargs)

    def print(self, msg, **kwargs):
        """Prints a message without any formatting."""
        self.console.print(msg, **kwargs)
