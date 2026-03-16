<div align="center">

# 🏔️ Sherpa

**Explains your terminal errors in plain English. Fully local, no API key.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/sherpa-dev.svg)](https://pypi.org/project/sherpa-dev/)

</div>

---

![Sherpa Demo](assets/demo.gif)

```
$ python app.py
TypeError: unsupported operand type(s) for +: 'int' and 'str'  [line 42]

$ sherpa

sherpa is thinking...

╭─ Why it failed ──────────────────────────────────────────────╮
│ You're trying to add an integer and a string at line 42.     │
│ Python requires both sides of + to be the same type —        │
│ it won't auto-convert like JavaScript does.                  │
╰──────────────────────────────────────────────────────────────╯
╭─ Fix ────────────────────────────────────────────────────────╮
│ total + int(user_input)                                      │
╰──────────────────────────────────────────────────────────────╯
```

## Install

```bash
pip install sherpa-dev
```

Or from source:

```bash
git clone https://github.com/RishiiGamer2201/sherpa
cd sherpa
pip install -e .
```

## First Run

```bash
sherpa
```

On first run, Sherpa will prompt you to download a local AI model (~4GB). After that, **everything runs offline** — no internet, no API key, no external server. Ever.

## Usage

```bash
# Explain last terminal error (default)
sherpa

# Explain a specific line in a file
sherpa explain app.py:42

# Ask a freeform question
sherpa ask why is my API returning 403 only in production

# Show current config
sherpa cfg show

# Switch to a different model
sherpa cfg set-model /path/to/custom-model.gguf
```

## Why Sherpa?

Every developer hits errors in their terminal every day. The usual workflow:

1. Read the error → feel confused
2. Copy the error → open browser → Google/ChatGPT → read results → come back

That's a context switch. You leave your flow, lose your mental state, and waste 3–5 minutes on something that should take 5 seconds.

**Sherpa eliminates that loop.** The explanation and fix come to you, right where the error happened.

> 🔒 **Your code never leaves your machine.** Sherpa runs entirely locally using a quantized AI model. No data is sent anywhere. Ever.

## How It Works

```
sherpa (you type this)
  │
  ├─ config.py    → checks if model exists
  ├─ setup.py     → downloads model on first run
  ├─ history.py   → reads last command + stderr from shell history
  ├─ ai.py        → loads local model, runs inference
  └─ display.py   → prints explanation + fix with rich styling
```

| Component | Library | Why |
|---|---|---|
| CLI | `click` | Clean command routing, auto help text |
| Output | `rich` | Colors, panels, syntax highlighting, progress bars |
| AI | `llama-cpp-python` | Runs `.gguf` models inline, no server needed |
| Model | CodeLlama 7B Q4 | Code-optimized, ~4GB, runs on CPU with 8GB RAM |

### Supported Models

| Model | Size | Best for |
|---|---|---|
| `codellama-7b-instruct.Q4_K_M.gguf` | 4GB | Default — code-specific, fast |
| `deepseek-coder-6.7b.Q4_K_M.gguf` | 4GB | Slightly better on debug tasks |
| `mistral-7b-instruct.Q4_K_M.gguf` | 4GB | Good general fallback |
| `gemma-2b-it.Q4_K_M.gguf` | 1.6GB | Low RAM machines (4GB or less) |
| `llama3.2-3b-instruct.Q4_K_M.gguf` | 2GB | Fast, decent quality, mid-range |

Switch models anytime:

```bash
sherpa cfg set-model /path/to/model.gguf
```

## Comparison

| Tool | Leaves Terminal? | Explains Why? | Works Offline? | Needs API Key? |
|---|---|---|---|---|
| **Sherpa** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| Stack Overflow | ✅ Yes | Sometimes | ❌ No | — |
| ChatGPT / Claude | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| GitHub Copilot | N/A (IDE) | ✅ Yes | ❌ No | ✅ Yes |
| `thefuck` | ❌ No | ❌ No | ✅ Yes | ❌ No |

## Supported Shells

- ✅ Bash
- ✅ Zsh
- ✅ Fish

## Requirements

- Python 3.10+
- 8GB RAM (for default 7B model)
- ~4GB disk space for the model

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for open tasks and guidelines.

## License

[MIT](LICENSE)

---

<div align="center">

*Built with Python and llama-cpp-python. Fully local. Your code never leaves your machine.*

</div>
