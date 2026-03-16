"""
First-run model download wizard.
When no model file is found, this runs a guided download
with a live progress bar using rich.
"""

import sys
import urllib.request
from pathlib import Path

from rich.console import Console
from rich.progress import (
    Progress,
    DownloadColumn,
    BarColumn,
    TransferSpeedColumn,
)

from sherpa.config import MODEL_URL, MODEL_PATH, SHERPA_DIR

console = Console()


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
