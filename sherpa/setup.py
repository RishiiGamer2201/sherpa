"""
First-run setup wizard.
Handles three things on first launch:
  1. Install llama-cpp-python with automatic fallbacks
  2. Show model picker — user chooses based on their RAM
  3. Download chosen model with a progress bar
"""

import sys
import subprocess
import urllib.request
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, DownloadColumn, BarColumn, TransferSpeedColumn
from rich import box

from sherpa.config import SHERPA_DIR, MODEL_PATH, MODELS, load, save

console = Console()


# ── llama-cpp-python installer ────────────────────────────────


def ensure_llama() -> bool:
    if _llama_importable():
        return True

    console.print("\n[bold]Setting up Sherpa for the first time...[/bold]\n")
    console.print(
        "[dim]Installing AI engine (llama-cpp-python). "
        "This only happens once.[/dim]\n"
    )

    console.print("[dim]Trying pre-built wheel...[/dim]")
    if _pip_install([
        "llama-cpp-python",
        "--extra-index-url",
        "https://abetlen.github.io/llama-cpp-python/whl/cpu",
        "--prefer-binary", "--quiet",
    ]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    console.print("[dim]Trying alternative wheel source...[/dim]")
    if _pip_install(["llama-cpp-python", "--prefer-binary", "--quiet"]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

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
    Print model list as plain lines (no table) so it renders
    correctly on any terminal width — narrow Kaggle cells, wide
    desktop terminals, Windows PowerShell, all work identically.
    Returns the chosen model dict.
    """
    console.print()
    console.print(Panel(
        "[bold]Choose a model[/bold] based on your available RAM.\n"
        "[dim]The model downloads once and is reused on every run.[/dim]",
        border_style="cyan",
        box=box.ROUNDED,
    ))
    console.print()

    for m in MODELS:
        console.print(
            f"  [bold cyan][{m['key']}][/bold cyan]  "
            f"[bold]{m['name']}[/bold]"
        )
        console.print(
            f"       Size: [yellow]{m['size']}[/yellow]   "
            f"RAM: [green]{m['ram']}[/green]"
        )
        console.print(f"       [dim]{m['best_for']}[/dim]")
        console.print()

    valid_keys = {m["key"] for m in MODELS}
    while True:
        choice = console.input(
            "[bold cyan]Enter model number [1-5]:[/bold cyan] "
        ).strip()
        if choice in valid_keys:
            break
        console.print(
            f"[red]Please enter a number between 1 and {len(MODELS)}.[/red]"
        )

    chosen = next(m for m in MODELS if m["key"] == choice)

    console.print()
    console.print(f"[bold]You chose:[/bold] {chosen['name']}")
    console.print(f"[dim]Size    :[/dim] {chosen['size']}")
    console.print(f"[dim]RAM     :[/dim] {chosen['ram']}")
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
