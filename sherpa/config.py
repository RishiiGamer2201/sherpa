"""
Manages the ~/.sherpa/ directory, config.json, and model path.
Everything Sherpa needs to know about its environment lives here.
"""

import json
from pathlib import Path

SHERPA_DIR  = Path.home() / ".sherpa"
CONFIG_FILE = SHERPA_DIR / "config.json"
MODEL_PATH  = SHERPA_DIR / "model.gguf"

# All supported models — shown to user on first run
MODELS = [
    {
        "key":         "1",
        "name":        "CodeLlama 7B Instruct (Q4)",
        "size":        "~4.0 GB",
        "ram":         "8 GB+",
        "best_for":    "Best quality — code errors, tracebacks, build failures",
        "url": (
            "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF"
            "/resolve/main/codellama-7b-instruct.Q4_K_M.gguf"
        ),
    },
    {
        "key":         "2",
        "name":        "Mistral 7B Instruct (Q4)",
        "size":        "~4.1 GB",
        "ram":         "8 GB+",
        "best_for":    "Great general errors, shell commands, config issues",
        "url": (
            "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
            "/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        ),
    },
    {
        "key":         "3",
        "name":        "Gemma 2B Instruct (Q4)",
        "size":        "~1.6 GB",
        "ram":         "4 GB+",
        "best_for":    "Low RAM machines — fast, decent quality",
        "url": (
            "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF"
            "/resolve/main/gemma-2-2b-it-Q4_K_M.gguf"
        ),
    },
    {
        "key":         "4",
        "name":        "Llama 3.2 3B Instruct (Q4)",
        "size":        "~2.0 GB",
        "ram":         "6 GB+",
        "best_for":    "Good balance of speed and quality on mid-range machines",
        "url": (
            "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF"
            "/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
        ),
    },
    {
        "key":         "5",
        "name":        "DeepSeek Coder 6.7B Instruct (Q4)",
        "size":        "~3.8 GB",
        "ram":         "8 GB+",
        "best_for":    "Best for pure code debugging, slightly better than CodeLlama",
        "url": (
            "https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF"
            "/resolve/main/deepseek-coder-6.7b-instruct.Q4_K_M.gguf"
        ),
    },
]

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
