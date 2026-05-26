"""Utility helpers for processing LLM output."""

from __future__ import annotations

import re


# Imports that are already available in the execution environment and
# should be stripped from extracted code to avoid redundant / conflicting loads.
_REDUNDANT_IMPORT_RE = re.compile(
    r"^\s*import\s+(pandas|numpy|matplotlib|seaborn)"
    r"|^\s*from\s+(pandas|numpy|matplotlib|seaborn)\s+import\s+",
    re.MULTILINE,
)


def extract_code_from_text(text: str) -> str:
    """Extract executable Python code from raw LLM output.

    Extraction strategy (first match wins):
    1. Fenced ``python ... `` block
    2. Generic fenced `` ... `` block
    3. Raw text (stripped)

    After extraction the code is cleaned:
    * Leading / trailing whitespace is removed.
    * Common redundant import lines (pandas, numpy, matplotlib, seaborn)
      are stripped because the execution sandbox pre-loads them.
    """

    # 1. ```python ... ```
    match = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        # 2. ``` ... ```
        match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            # 3. Raw text
            code = text

    code = code.strip()

    # Remove redundant import lines
    cleaned_lines = [
        line
        for line in code.splitlines()
        if not _REDUNDANT_IMPORT_RE.match(line)
    ]

    return "\n".join(cleaned_lines).strip()
