"""
Reads shell history to identify the last command that was run,
then re-runs it to capture its stderr output.
Supports bash, zsh, fish, and PowerShell (live session history via Get-History).
"""

import os
import sys
import subprocess
from pathlib import Path

# Commands shorter than this are almost certainly fragments — skip them
_MIN_CMD_LENGTH = 4

# Prefixes to always skip — these are never real errors to explain
_SKIP_PREFIXES = (
    "sherpa",
    "python -m sherpa",
    "python -c",
    "deactivate",
    "activate",
    ".venv",
    "& c:\\",
    "& c:/",
    "git ",
    "cd ",
    "ls",
    "dir",
    "clear",
    "cls",
    "echo",
    "cat ",
    "type ",
    "get-",
    "set-",
    "test-path",
    "write-host",
    "select-",
    "remove-",
    "copy-",
    "move-",
    "#",       # shell comments — never a real command
    ">>",      # PowerShell multiline continuation prompts
    "& ",      # PowerShell call operator lines
)


def _is_valid_command(cmd: str) -> bool:
    """Return True only if cmd looks like a real runnable command."""
    cmd = cmd.strip()
    if not cmd:
        return False
    # Too short — likely a fragment (a lone quote or bracket)
    if len(cmd) < _MIN_CMD_LENGTH:
        return False
    # Contains only quotes/brackets/whitespace — definitely a fragment
    if all(c in '"\'()[]{}' for c in cmd):
        return False
    lower = cmd.lower()
    for prefix in _SKIP_PREFIXES:
        if lower.startswith(prefix.lower()):
            return False
    return True


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
    if sys.platform == "win32":
        if os.environ.get("PSModulePath"):
            return "powershell"
        return "cmd"

    shell_path = os.environ.get("SHELL", "")
    if "zsh"  in shell_path: return "zsh"
    if "fish" in shell_path: return "fish"
    return "bash"


def _last_command(shell: str) -> str:
    """Read the last valid non-sherpa command from shell history."""
    if shell == "powershell":
        return _last_powershell_command()
    if shell == "cmd":
        return ""

    history_file = {
        "bash": Path.home() / ".bash_history",
        "zsh":  Path.home() / ".zsh_history",
        "fish": Path.home() / ".local" / "share" / "fish" / "fish_history",
    }.get(shell, Path.home() / ".bash_history")

    if not history_file.exists():
        return ""

    lines = history_file.read_text(errors="ignore").strip().splitlines()

    if shell == "zsh":
        lines = [
            l.split(";", 1)[-1] if l.startswith(":") else l
            for l in lines
        ]

    if shell == "fish":
        lines = [
            l.replace("- cmd:", "").strip()
            for l in lines if l.strip().startswith("- cmd:")
        ]

    for line in reversed(lines):
        if _is_valid_command(line):
            return line.strip()

    return ""


def _last_powershell_command() -> str:
    """
    Read live PowerShell session history using Get-History.
    Falls back to the PSReadLine file if Get-History is unavailable.
    """
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-NonInteractive", "-Command",
                "(Get-History | Select-Object -Last 30 | "
                "Select-Object -ExpandProperty CommandLine) -join '|||'"
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            commands = result.stdout.strip().split("|||")
            for cmd in reversed(commands):
                if _is_valid_command(cmd):
                    return cmd.strip()

    except Exception:
        pass

    # Fallback: PSReadLine history file (previous sessions)
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
            if _is_valid_command(line):
                return line.strip()

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
