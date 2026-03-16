"""
Reads shell history to identify the last command that was run,
then re-runs it to capture its stderr output.
Supports bash, zsh, fish, and PowerShell (live session history via Get-History).
"""

import os
import sys
import subprocess
from pathlib import Path


def get_last_error() -> dict:
    """
    Returns dict with keys:
      command  — the command that was run
      stderr   — the error output
      shell    — detected shell name
    """
    shell   = _detect_shell()
    command = _last_command(shell)
    stderr  = _capture_stderr(command)
    return {"command": command, "stderr": stderr, "shell": shell}


def _detect_shell() -> str:
    """
    Detect the user's current shell.
    On Windows, PSModulePath is always set inside a PowerShell session.
    On Unix, read the SHELL env variable.
    """
    # Windows PowerShell / pwsh detection
    # PSModulePath is injected by PowerShell itself — not present in cmd.exe
    if sys.platform == "win32":
        if os.environ.get("PSModulePath"):
            return "powershell"
        return "cmd"   # fallback for cmd.exe

    # Unix
    shell_path = os.environ.get("SHELL", "")
    if "zsh"  in shell_path: return "zsh"
    if "fish" in shell_path: return "fish"
    return "bash"


def _last_command(shell: str) -> str:
    """Read the last non-sherpa command from shell history."""
    if shell == "powershell":
        return _last_powershell_command()
    if shell == "cmd":
        return ""   # cmd.exe has no accessible history file

    history_file = {
        "bash": Path.home() / ".bash_history",
        "zsh":  Path.home() / ".zsh_history",
        "fish": Path.home() / ".local" / "share" / "fish" / "fish_history",
    }.get(shell, Path.home() / ".bash_history")

    if not history_file.exists():
        return ""

    lines = history_file.read_text(errors="ignore").strip().splitlines()

    # zsh prefixes lines with ": timestamp:0;" — strip it
    if shell == "zsh":
        lines = [
            l.split(";", 1)[-1] if l.startswith(":") else l
            for l in lines
        ]

    # fish uses "- cmd:" format
    if shell == "fish":
        lines = [
            l.replace("- cmd:", "").strip()
            for l in lines if l.strip().startswith("- cmd:")
        ]

    # walk backwards, skip blank lines and sherpa itself
    for line in reversed(lines):
        line = line.strip()
        if line and not line.startswith("sherpa"):
            return line

    return ""


def _last_powershell_command() -> str:
    """
    Read live PowerShell session history using Get-History.
    This works during the current session -- unlike the PSReadLine
    history file, which is only flushed when the session ends.
    Falls back to the PSReadLine file if Get-History is unavailable.
    """
    try:
        # Get-History returns commands in order, oldest first.
        # We select the last 20 and walk backwards to skip sherpa calls.
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-NonInteractive", "-Command",
                "(Get-History | Select-Object -Last 20 | "
                "Select-Object -ExpandProperty CommandLine) -join '|||'"
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            commands = result.stdout.strip().split("|||")
            for cmd in reversed(commands):
                cmd = cmd.strip()
                if cmd and not cmd.lower().startswith("sherpa"):
                    return cmd

    except Exception:
        pass  # fall through to file-based fallback

    # Fallback: PSReadLine history file (previous sessions only)
    ps_history = (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "PowerShell"
        / "PSReadLine"
        / "ConsoleHost_history.txt"
    )
    if ps_history.exists():
        lines = ps_history.read_text(errors="ignore").strip().splitlines()
        for line in reversed(lines):
            line = line.strip()
            if line and not line.lower().startswith("sherpa"):
                return line

    return ""


def _capture_stderr(command: str) -> str:
    """Re-run the last command and capture its stderr."""
    if not command:
        return ""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (result.stderr or result.stdout or "").strip()
    except Exception as e:
        return str(e)
