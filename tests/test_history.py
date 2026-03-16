"""
Tests for sherpa.history module.
Tests shell detection, history file parsing, and command skipping.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from sherpa.history import _detect_shell, _last_command


# ─── Shell detection ─────────────────────────────────────────


class TestDetectShell:
    def test_detects_zsh(self):
        with mock.patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
            assert _detect_shell() == "zsh"

    def test_detects_bash(self):
        with mock.patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            assert _detect_shell() == "bash"

    def test_detects_fish(self):
        with mock.patch.dict(os.environ, {"SHELL": "/usr/bin/fish"}):
            assert _detect_shell() == "fish"

    def test_defaults_to_bash_when_empty(self):
        with mock.patch.dict(os.environ, {"SHELL": ""}, clear=False):
            # Should return bash or powershell depending on COMSPEC
            result = _detect_shell()
            assert result in ("bash", "powershell")


# ─── Last command parsing ─────────────────────────────────────


class TestLastCommand:
    def test_reads_bash_history(self, tmp_path):
        hist = tmp_path / ".bash_history"
        hist.write_text("ls\npython app.py\nsherpa\n")

        with mock.patch("sherpa.history.Path.home", return_value=tmp_path):
            cmd = _last_command("bash")
        assert cmd == "python app.py"

    def test_reads_zsh_history(self, tmp_path):
        hist = tmp_path / ".zsh_history"
        hist.write_text(
            ": 1700000001:0;cd project\n"
            ": 1700000002:0;python main.py\n"
            ": 1700000003:0;sherpa\n"
        )

        with mock.patch("sherpa.history.Path.home", return_value=tmp_path):
            cmd = _last_command("zsh")
        assert cmd == "python main.py"

    def test_reads_fish_history(self, tmp_path):
        fish_dir = tmp_path / ".local" / "share" / "fish"
        fish_dir.mkdir(parents=True)
        hist = fish_dir / "fish_history"
        hist.write_text(
            "- cmd: git status\n"
            "  when: 1700000001\n"
            "- cmd: npm start\n"
            "  when: 1700000002\n"
            "- cmd: sherpa\n"
            "  when: 1700000003\n"
        )

        with mock.patch("sherpa.history.Path.home", return_value=tmp_path):
            cmd = _last_command("fish")
        assert cmd == "npm start"

    def test_skips_sherpa_commands(self, tmp_path):
        hist = tmp_path / ".bash_history"
        hist.write_text("make build\nsherpa\nsherpa ask why\n")

        with mock.patch("sherpa.history.Path.home", return_value=tmp_path):
            cmd = _last_command("bash")
        assert cmd == "make build"

    def test_returns_empty_when_no_history(self, tmp_path):
        with mock.patch("sherpa.history.Path.home", return_value=tmp_path):
            cmd = _last_command("bash")
        assert cmd == ""

    def test_skips_blank_lines(self, tmp_path):
        hist = tmp_path / ".bash_history"
        hist.write_text("cargo run\n\n\n\n")

        with mock.patch("sherpa.history.Path.home", return_value=tmp_path):
            cmd = _last_command("bash")
        assert cmd == "cargo run"
