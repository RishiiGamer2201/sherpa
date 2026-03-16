"""
First-run setup wizard.
Handles two things on first launch:
  1. Install llama-cpp-python with automatic fallbacks (no compiler needed)
  2. Download the CodeLlama model with a progress bar
"""

import sys
import subprocess
import urllib.request
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, DownloadColumn, BarColumn, TransferSpeedColumn
from rich.panel import Panel

from sherpa.config import MODEL_URL, MODEL_PATH, SHERPA_DIR

console = Console()


# ── llama-cpp-python installer ────────────────────────────────


def ensure_llama() -> bool:
    """
    Returns True if llama-cpp-python is already installed or gets
    installed successfully. Returns False if all methods fail.
    """
    # Already installed — nothing to do
    if _llama_importable():
        return True

    console.print(
        "\n[bold]Setting up Sherpa for the first time...[/bold]\n"
    )
    console.print(
        "[dim]Installing AI engine (llama-cpp-python).[/dim] "
        "This only happens once.\n"
    )

    # Method 1 — pre-built CPU wheel index (works for Python 3.10–3.12)
    console.print("[dim]Trying pre-built wheel...[/dim]")
    if _pip_install([
        "llama-cpp-python",
        "--extra-index-url",
        "https://abetlen.github.io/llama-cpp-python/whl/cpu",
        "--prefer-binary",
        "--quiet",
    ]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    # Method 2 — prefer-binary from PyPI only (sometimes works on 3.13)
    console.print("[dim]Trying alternative wheel source...[/dim]")
    if _pip_install([
        "llama-cpp-python",
        "--prefer-binary",
        "--quiet",
    ]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    # Method 3 — build from source (needs C++ compiler)
    console.print("[dim]Trying to build from source...[/dim]")
    if _pip_install(["llama-cpp-python", "--quiet"]):
        console.print("[green]✓ AI engine installed.[/green]\n")
        return True

    # All methods failed — show a clear human-friendly message
    _show_install_help()
    return False


def _llama_importable() -> bool:
    """Check if llama_cpp is importable without actually loading a model."""
    try:
        import importlib
        importlib.import_module("llama_cpp")
        return True
    except ImportError:
        return False


def _pip_install(args: list) -> bool:
    """Run pip install with the given args. Returns True on success."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + args,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def _show_install_help():
    """Show a clear, friendly error message with exact steps to fix."""
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"

    console.print(Panel(
        f"""[bold yellow]One manual step required.[/bold yellow]

Sherpa's AI engine couldn't install automatically on Python {py_ver}.
This is a known issue and takes about 10 minutes to fix.

[bold]Step 1[/bold] — Download and install the C++ Build Tools:
[cyan]https://aka.ms/vs/17/release/vs_BuildTools.exe[/cyan]

[bold]Step 2[/bold] — In the installer, tick:
  [green]✓ Desktop development with C++[/green]

[bold]Step 3[/bold] — After it finishes, close this terminal,
  open a new one, and run [bold]sherpa[/bold] again.

That's it — Sherpa will continue setup automatically.""",
        title="[bold]Setup needed[/bold]",
        border_style="yellow",
    ))
    sys.exit(1)


# ── Model downloader ──────────────────────────────────────────


def download_model():
    """Prompt user to download the default CodeLlama model."""
    SHERPA_DIR.mkdir(exist_ok=True)

    console.print(
        "\n[bold]No model found.[/bold] "
        "Sherpa needs a local AI model to work.\n"
    )
    console.print(f"[dim]Model   :[/dim] CodeLlama 7B Instruct (Q4 — ~4GB)")
    console.print(f"[dim]Saved to:[/dim] {MODEL_PATH}\n")

    confirm = console.input("Download now? [y/N] ").strip().lower()
    if confirm != "y":
        console.print(
            "[yellow]Aborted. Run `sherpa` again when ready.[/yellow]"
        )
        sys.exit(0)

    console.print()

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:
        task = progress.add_task("Downloading model...", total=None)

        def reporthook(count, block_size, total_size):
            if total_size > 0:
                progress.update(
                    task, total=total_size, completed=count * block_size
                )

        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook)

    console.print(
        "\n[green]Model downloaded.[/green] "
        "Run `sherpa` to explain your last error.\n"
    )
