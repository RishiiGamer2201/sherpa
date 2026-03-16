# Contributing to Sherpa

Thanks for your interest in contributing! Sherpa is a simple project with a clear architecture, so getting started should be straightforward.

## Setup

```bash
git clone https://github.com/RishiiGamer2201/sherpa
cd sherpa
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Architecture

```
sherpa/
  cli.py        ← entry point, routes all commands
  history.py    ← reads shell history, captures last error
  ai.py         ← loads local model, runs inference, parses response
  display.py    ← formats and prints output using rich
  config.py     ← manages ~/.sherpa/config.json and model path
  setup.py      ← first-run model download wizard
```

Each file has a single, isolated responsibility.

## Open Tasks

These are clearly scoped tasks that make great first contributions:

### 🟢 Good First Issues

- [ ] **Add `--brief` flag** — One-line answer mode. Skip the panels, just print a single sentence.
- [ ] **Add `--model` flag** — Override model per-command without changing config permanently.
- [ ] **Add `--lang` flag** — Force a specific programming language context in the prompt.
- [ ] **Add pipe support** — Allow `cat error.log | sherpa` to read errors from stdin.

### 🟡 Medium

- [ ] **Add native Windows PowerShell support** — Read PowerShell history (`Get-History` or `(Get-PSReadlineOption).HistorySavePath`), handle Windows paths.
- [ ] **Improve fish shell history parsing** — Handle multiline commands, test with real fish history files.
- [ ] **Add `sherpa watch` mode** — Monitor terminal output automatically and explain errors as they happen.
- [ ] **Add shell integration** — Automatic error capture via shell hooks (`PROMPT_COMMAND` for bash, `precmd` for zsh).

### 🔴 Advanced

- [ ] **Package for Homebrew** — Create a Homebrew formula for `brew install sherpa`.
- [ ] **Package for `pipx`** — Ensure clean `pipx install sherpa-dev` workflow.
- [ ] **Write integration tests** — Full end-to-end tests for all three shell history parsers.
- [ ] **Add model benchmarking** — Compare different GGUF models on a standard set of error messages.

## Code Style

- Python 3.10+ (use `match` statements where appropriate)
- Type hints on all public functions
- Docstrings on all modules and public functions
- Run `pytest` before submitting a PR

## Pull Request Process

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Add tests if applicable
4. Run `python -m pytest tests/ -v`
5. Submit a PR with a clear description of what you changed and why

## Questions?

Open an issue or start a discussion. We're happy to help!
