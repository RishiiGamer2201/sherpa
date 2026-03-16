"""
CLI entry point for Sherpa.
Routes commands: default (explain last error), explain (specific line),
ask (freeform question), and cfg (configuration management).
"""

import sys
import click
from rich.console import Console

from sherpa import config, setup, history, ai, display

console = Console()


def _strip_windows_argv_bug():
    """
    On Windows editable installs, the .exe wrapper sometimes injects its own
    path into sys.argv[1], causing click to treat it as a subcommand.
    Strip it if detected.
    """
    if len(sys.argv) > 1 and sys.argv[1].endswith(".exe"):
        sys.argv.pop(1)


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Sherpa — explains your terminal errors. Fully local, no API key."""
    _strip_windows_argv_bug()
    if ctx.invoked_subcommand is None:
        _explain_last()


@main.command()
@click.argument("target")   # format: file.py:42
def explain(target):
    """Explain a specific line. Usage: sherpa explain app.py:42"""
    _ensure_model()
    try:
        filepath, line = target.rsplit(":", 1)
        line_number = int(line)
    except ValueError:
        display.show_error(
            "Format must be file.py:LINE — e.g. sherpa explain app.py:42"
        )
        return
    display.show_thinking()
    result = ai.explain_line(filepath, line_number)
    display.show_result(result)


@main.command()
@click.argument("question", nargs=-1)
def ask(question):
    """Ask anything. Usage: sherpa ask why is my loop infinite"""
    _ensure_model()
    q = " ".join(question)
    if not q:
        display.show_error(
            "Provide a question. e.g. sherpa ask why is my dict empty"
        )
        return
    display.show_thinking()
    result = ai.ask_question(q)
    display.show_result(result)


@main.group()
def cfg():
    """Manage sherpa config."""
    pass


@cfg.command("show")
def cfg_show():
    """Show current config."""
    import json
    c = config.load()
    console.print_json(json.dumps(c))


@cfg.command("set-model")
@click.argument("path")
def cfg_set_model(path):
    """Point sherpa to a different .gguf model file."""
    c = config.load()
    c["model_path"] = path
    config.save(c)
    console.print(f"[green]Model path updated to:[/green] {path}")


# ─── Internal helpers ────────────────────────────────────────


def _ensure_model():
    """Trigger download wizard if no model is found."""
    if not config.model_exists():
        setup.download_model()
        raise SystemExit(0)


def _explain_last():
    """Default command — explain the last terminal error."""
    _ensure_model()
    err = history.get_last_error()

    if not err["command"]:
        display.show_error(
            "Could not read shell history. "
            "Run a command first, then try `sherpa` again."
        )
        return

    if not err["stderr"]:
        display.show_error(
            f"No error output found for: {err['command']}"
        )
        return

    display.show_thinking()
    result = ai.explain(err["command"], err["stderr"])
    display.show_result(result, command=err["command"])
