"""
The AI engine. Loads the GGUF model once via llama-cpp-python and
caches it for the lifetime of the process. Sends structured prompts
to the model and parses responses into {"reason": ..., "fix": ...} dicts.
"""

from sherpa.config import load

_llm = None  # loaded once, reused across calls


def _get_model():
    """Load the model on first call, reuse on subsequent calls."""
    global _llm
    if _llm is None:
        from llama_cpp import Llama
        from rich.console import Console
        console = Console()
        console.print(
            "[dim]Loading model into memory "
            "(this takes 30-60 seconds on first run)...[/dim]"
        )
        cfg = load()
        _llm = Llama(
            model_path=cfg["model_path"],
            n_ctx=cfg["n_ctx"],
            verbose=cfg["verbose"],
        )
    return _llm


SYSTEM_PROMPT = """\
You are a senior developer assistant embedded in a terminal.
When given a shell command and its error output, you:
1. Explain in 2-3 plain English sentences WHY the error happened.
2. Give ONE exact, copy-pasteable fix.
3. Never give walls of text. Be direct and specific.
Format your response exactly like this:
REASON: <why it failed>
FIX: <exact code or command fix>
"""


def explain(command: str, stderr: str) -> dict:
    """Explain a terminal error from a command and its stderr."""
    llm = _get_model()
    prompt = f"""{SYSTEM_PROMPT}

Command: {command}
Error:
{stderr}

Response:"""

    output = llm(
        prompt,
        max_tokens=load()["max_tokens"],
        stop=["Command:", "Error:", "\n\n\n"],
        echo=False,
    )

    raw = output["choices"][0]["text"].strip()
    return _parse(raw)


def explain_line(filepath: str, line_number: int) -> dict:
    """Explain a specific line of code in a file."""
    try:
        lines   = open(filepath).readlines()
        start   = max(0, line_number - 4)
        end     = min(len(lines), line_number + 3)
        snippet = "".join(lines[start:end])
        target  = lines[line_number - 1].strip()
    except Exception as e:
        return {"reason": str(e), "fix": "Check the file path and line number."}

    llm = _get_model()
    prompt = f"""{SYSTEM_PROMPT}

File: {filepath}, line {line_number}
Line in question: {target}
Context:
{snippet}

Response:"""

    output = llm(
        prompt, max_tokens=load()["max_tokens"], stop=["\n\n\n"], echo=False
    )
    return _parse(output["choices"][0]["text"].strip())


def ask_question(question: str) -> dict:
    """Answer a freeform developer question."""
    llm = _get_model()
    prompt = f"""{SYSTEM_PROMPT}

Developer question: {question}

Response:"""

    output = llm(
        prompt, max_tokens=load()["max_tokens"], stop=["\n\n\n"], echo=False
    )
    return _parse(output["choices"][0]["text"].strip())


def _parse(raw: str) -> dict:
    """Parse model output into {reason, fix} dict."""
    reason, fix = "", ""
    for line in raw.splitlines():
        if line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[-1].strip()
        elif line.upper().startswith("FIX:"):
            fix = line.split(":", 1)[-1].strip()
    if not reason:
        reason = raw
    return {"reason": reason, "fix": fix}
