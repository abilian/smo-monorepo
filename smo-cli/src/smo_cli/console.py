import rich.console


class Console:
    def __init__(self, verbosity: int = 0):
        self.verbosity = verbosity
        self.console = rich.console.Console()

    def info(self, *args, **kwargs):
        """Print a message only if verbosity is 1 or more."""
        if self.verbosity >= 1:
            self.console.print(*args, **kwargs)

    def debug(self, *args, **kwargs):
        """Print a message only if verbosity is 2 or more."""
        if self.verbosity >= 2:
            self.console.print(f"[dim]DEBUG:[/] ", *args, **kwargs, style="grey70")

    def error(self, *args, **kwargs):
        """Print an error message."""
        self.console.print(f"[bold red]ERROR:[/] ", *args, **kwargs)

    def warning(self, *args, **kwargs):
        """Print a warning message."""
        self.console.print(f"[bold yellow]WARNING:[/] ", *args, **kwargs)

    def success(self, *args, **kwargs):
        """Print a success message."""
        self.console.print(f"[bold green]SUCCESS:[/] ", *args, **kwargs)

    def print(self, *args, **kwargs):
        """Prints a message without any formatting."""
        self.console.print(*args, **kwargs)
