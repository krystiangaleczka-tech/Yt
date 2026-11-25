"""Call whichever AI the user chose (Claude Code, Codex, Gemini, Kimi, OpenCode, Ollama, custom).

Each backend is a command template from settings["ai_commands"]:
  {prompt_text}  -> replaced by the whole prompt as one argument
  {prompt_file}  -> replaced by a path to a file holding the prompt
  neither        -> the prompt goes to stdin
"""
from __future__ import annotations

import json
import re
import shlex
import shutil
import sys
import tempfile
from pathlib import Path

from .util import ToolError, run


def available(settings: dict) -> bool:
    name = settings.get("ai", "none")
    if name == "none":
        return False
    tpl = settings["ai_commands"].get(name, "")
    if not tpl:
        return False
    exe = shlex.split(tpl, posix=sys.platform != "win32")[0]
    return shutil.which(exe) is not None


def ask(settings: dict, prompt: str, timeout: int = 1200) -> str:
    name = settings.get("ai", "none")
    tpl = settings["ai_commands"].get(name, "")
    if name == "none" or not tpl:
        raise ToolError("Nie wybrano AI (Ustawienia → AI).")
    parts = shlex.split(tpl, posix=sys.platform != "win32")
    exe = shutil.which(parts[0]) or parts[0]
    pf = None
    stdin = prompt
    args = [exe]
    for p in parts[1:]:
        if "{prompt_text}" in p:
            args.append(p.replace("{prompt_text}", prompt))
            stdin = None
        elif "{prompt_file}" in p:
            if pf is None:
                pf = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
                pf.write(prompt)
                pf.close()
            args.append(p.replace("{prompt_file}", pf.name))
            stdin = None
        else:
            args.append(p)
    try:
        r = run(args, timeout=timeout, input_text=stdin)
    finally:
        if pf:
            Path(pf.name).unlink(missing_ok=True)
    return r.stdout


def extract_json(text: str):
    """Pull the first JSON array/object out of an AI answer (handles ```json fences)."""
    m = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    if m:
        text = m.group(1)
    for open_, close in (("[", "]"), ("{", "}")):
        a, b = text.find(open_), text.rfind(close)
        if a != -1 and b > a:
            try:
                return json.loads(text[a:b + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("AI nie zwróciło poprawnego JSON")
