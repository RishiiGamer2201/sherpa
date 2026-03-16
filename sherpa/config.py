"""
Manages the ~/.sherpa/ directory, config.json, and model path.
Everything Sherpa needs to know about its environment lives here.
"""

import json
import os
from pathlib import Path

SHERPA_DIR   = Path.home() / ".sherpa"
CONFIG_FILE  = SHERPA_DIR / "config.json"
MODEL_PATH   = SHERPA_DIR / "model.gguf"

MODEL_URL = (
    "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF"
    "/resolve/main/codellama-7b-instruct.Q4_K_M.gguf"
)

DEFAULTS = {
    "model_path": str(MODEL_PATH),
    "n_ctx":      2048,
    "max_tokens": 350,
    "verbose":    False,
}


def load() -> dict:
    """Load config from ~/.sherpa/config.json, creating defaults if needed."""
    SHERPA_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        save(DEFAULTS)
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save(cfg: dict):
    """Save config dict to ~/.sherpa/config.json."""
    SHERPA_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def model_exists() -> bool:
    """Check if the configured model file exists on disk."""
    cfg = load()
    return Path(cfg["model_path"]).exists()
