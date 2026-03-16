"""
Handles all terminal output using rich.
Colored panels, syntax-highlighted code, and clean visual separation.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich import box

console = Console()


def show_result(result: dict, command: str = ""):
    """Display the explanation and fix in styled panels."""
    console.print()

    if command:
        console.print(f"[dim]Command:[/dim] [bold]{command}[/bold]\n")

    reason_text = Text(result["reason"])
    console.print(Panel(
        reason_text,
        title="[bold yellow]Why it failed[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1),
    ))

    if result.get("fix"):
        fix = result["fix"]
        # detect if fix looks like code or a plain sentence
        if any(c in fix for c in ["(", "=", "->", "import", "$", "."]):
            syntax = Syntax(fix, "python", theme="monokai", word_wrap=True)
            console.print(Panel(
                syntax,
                title="[bold green]Fix[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
            ))
        else:
            console.print(Panel(
                Text(fix, style="green"),
                title="[bold green]Fix[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
            ))

    console.print()


def show_error(message: str):
    """Display an error message in red."""
    console.print(f"\n[bold red]Error:[/bold red] {message}\n")


def show_thinking():
    """Display a thinking indicator."""
    console.print("\n[dim]sherpa is thinking...[/dim]")
