"""
Tests for sherpa.ai module.
Tests response parsing and prompt construction (model is mocked).
"""

import pytest
from unittest import mock

from sherpa.ai import _parse


# ─── Response parsing ─────────────────────────────────────────


class TestParse:
    def test_parses_standard_format(self):
        raw = "REASON: You have a typo in the variable name.\nFIX: x = 42"
        result = _parse(raw)
        assert result["reason"] == "You have a typo in the variable name."
        assert result["fix"] == "x = 42"

    def test_parses_case_insensitive(self):
        raw = "reason: Missing import statement.\nfix: import os"
        result = _parse(raw)
        assert result["reason"] == "Missing import statement."
        assert result["fix"] == "import os"

    def test_fallback_when_no_markers(self):
        raw = "The error is caused by a missing semicolon."
        result = _parse(raw)
        assert result["reason"] == raw
        assert result["fix"] == ""

    def test_handles_empty_string(self):
        result = _parse("")
        assert result["reason"] == ""
        assert result["fix"] == ""

    def test_handles_multiline_reason(self):
        raw = (
            "REASON: The file does not exist at the given path.\n"
            "FIX: touch /tmp/data.csv"
        )
        result = _parse(raw)
        assert "file does not exist" in result["reason"]
        assert result["fix"] == "touch /tmp/data.csv"

    def test_reason_only_no_fix(self):
        raw = "REASON: Permission denied when accessing /etc/shadow."
        result = _parse(raw)
        assert result["reason"] == "Permission denied when accessing /etc/shadow."
        assert result["fix"] == ""

    def test_extra_whitespace(self):
        raw = "REASON:   spaces everywhere   \nFIX:   pip install requests   "
        result = _parse(raw)
        assert result["reason"] == "spaces everywhere"
        assert result["fix"] == "pip install requests"


# ─── Explain function (mocked model) ─────────────────────────


class TestExplain:
    @mock.patch("sherpa.ai._get_model")
    @mock.patch("sherpa.ai.load", return_value={"max_tokens": 350})
    def test_explain_calls_model(self, mock_load, mock_model):
        fake_llm = mock.MagicMock()
        fake_llm.return_value = {
            "choices": [{"text": "REASON: Bad import\nFIX: import sys"}]
        }
        mock_model.return_value = fake_llm

        from sherpa.ai import explain
        result = explain("python app.py", "ModuleNotFoundError: No module named 'sys2'")

        assert result["reason"] == "Bad import"
        assert result["fix"] == "import sys"
        fake_llm.assert_called_once()
