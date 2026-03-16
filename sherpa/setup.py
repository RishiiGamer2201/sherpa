"""
First-run setup wizard.
Handles two things on first launch:
  1. Install llama-cpp-python with automatic fallbacks
  2. Show model picker — user chooses based on their RAM
  3. Download chosen model with a progress bar
"""

import sys
import subprocess
import urllib.request
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, DownloadColumn, BarColumn, TransferSpeedColumn
from rich import box

from sherpa.config import SHERPA_DIR, MODEL_PATH, MODELS, load, save

console = Console()


# ── llama-cpp-python installer ────────────────────────────────


def ensure_llama() -> bool:
    """
    Returns True if llama-cpp-python is already installed or
    gets installed successfully. Returns False if all methods fail.
    """
    if _llama_importable():
        return True

    console.print(
        "\n[bold]Setting up Sherpa for the first time...[/bold]\n"
    )
    console.print(
        "[dim]Installing AI engine (llama-cpp-python). "
        "This only happens once.[/dim]\n"
    )

    # Method 1 — pre-built CPU wheel index (Python 3.10–3.12)
    console.print("[dim]Trying pre-built wheel...[/dim]")
    if _pip_install([
        "llama-cpp-python",
        "--extra-index-url",
        "https://abetlen.github.io/llama-cpp-python/whl/cpu",
        "--prefer-binary", "--quiet",
    ]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    # Method 2 — prefer-binary from PyPI
    console.print("[dim]Trying alternative wheel source...[/dim]")
    if _pip_install(["llama-cpp-python", "--prefer-binary", "--quiet"]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    # Method 3 — build from source
    console.print("[dim]Trying to build from source...[/dim]")
    if _pip_install(["llama-cpp-python", "--quiet"]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    _show_install_help()
    return False


def _llama_importable() -> bool:
    try:
        import importlib
        importlib.import_module("llama_cpp")
        return True
    except ImportError:
        return False


def _pip_install(args: list) -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + args,
            capture_output=True, text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def _show_install_help():
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    console.print(Panel(
        f"""[bold yellow]One manual step required.[/bold yellow]

Sherpa's AI engine couldn't install automatically on Python {py_ver}.
This takes about 10 minutes to fix.

[bold]Step 1[/bold] — Download Visual Studio Build Tools:
[cyan]https://aka.ms/vs/17/release/vs_BuildTools.exe[/cyan]

[bold]Step 2[/bold] — In the installer tick:
  [green]✓ Desktop development with C++[/green]

[bold]Step 3[/bold] — Close this terminal, open a new one,
  and run [bold]python -m sherpa[/bold] again.""",
        title="[bold]Setup needed[/bold]",
        border_style="yellow",
    ))
    sys.exit(1)


# ── Model picker ──────────────────────────────────────────────


def pick_model() -> dict:
    """
    Show the model table and let the user pick by number.
    Returns the chosen model dict from MODELS.
    """
    console.print()
    console.print(
        Panel(
            "[bold]Choose a model[/bold] based on your available RAM.\n"
            "[dim]The model downloads once and is reused on every run.[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    console.print()

    # Build the table
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 1),
    )
    table.add_column("#",        style="bold cyan",   width=3,  justify="center")
    table.add_column("Model",    style="bold white",  width=32)
    table.add_column("Size",     style="yellow",      width=10, justify="center")
    table.add_column("RAM",      style="green",       width=8,  justify="center")
    table.add_column("Best for", style="dim white",   width=48)

    for m in MODELS:
        table.add_row(
            m["key"],
            m["name"],
            m["size"],
            m["ram"],
            m["best_for"],
        )

    console.print(table)
    console.print()

    # Get valid choice
    valid_keys = {m["key"] for m in MODELS}
    while True:
        choice = console.input(
            "[bold cyan]Enter model number [1-5]:[/bold cyan] "
        ).strip()
        if choice in valid_keys:
            break
        console.print(
            f"[red]Invalid choice '{choice}'. "
            f"Please enter a number between 1 and {len(MODELS)}.[/red]"
        )

    chosen = next(m for m in MODELS if m["key"] == choice)

    # Confirm
    console.print()
    console.print(f"[bold]You chose:[/bold] {chosen['name']}")
    console.print(f"[dim]Size    :[/dim] {chosen['size']}")
    console.print(f"[dim]Saved to:[/dim] {MODEL_PATH}")
    console.print()

    while True:
        confirm = console.input(
            "Download now? [bold][y/n][/bold]: "
        ).strip().lower()
        if confirm in ("y", "yes"):
            return chosen
        if confirm in ("n", "no"):
            console.print(
                "[yellow]Aborted. Run `python -m sherpa` again when ready.[/yellow]"
            )
            sys.exit(0)
        console.print("[red]Please type y or n.[/red]")


# ── Model downloader ──────────────────────────────────────────


def download_model():
    """Show model picker then download the chosen model."""
    SHERPA_DIR.mkdir(exist_ok=True)

    chosen = pick_model()

    console.print()
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:
        task = progress.add_task(
            f"Downloading {chosen['name']}...", total=None
        )

        def reporthook(count, block_size, total_size):
            if total_size > 0:
                progress.update(
                    task, total=total_size, completed=count * block_size
                )

        urllib.request.urlretrieve(chosen["url"], MODEL_PATH, reporthook)

    console.print(
        f"\n[green]✓ {chosen['name']} downloaded.[/green] "
        "Run [bold]python -m sherpa[/bold] to explain your last error.\n"
    )
