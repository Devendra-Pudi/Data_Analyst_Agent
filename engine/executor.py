"""
executor.py – Safe(r) code execution sandbox for the AI Data Analyst.

Executes an arbitrary Python code string inside a restricted namespace that
has access to *df*, *pd*, *np*, *plt*, and *sns*.  Output is captured and
returned as a typed dictionary suitable for rendering in the Streamlit UI.
"""

from __future__ import annotations

import io
import sys
import tempfile
import threading
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def execute_code(df: pd.DataFrame, code: str, timeout: int = 30) -> dict:
    """Execute *code* against a DataFrame and return structured output.

    Parameters
    ----------
    df : pd.DataFrame
        The user's active dataset, available as ``df`` inside the code.
    code : str
        Python source code to execute.
    timeout : int, optional
        Maximum wall-clock seconds before the execution is interrupted
        (default **30**).

    Returns
    -------
    dict
        Always contains ``"code"`` (the original source) plus ``"type"``
        and ``"data"``:

        * ``{"type": "dataframe", "data": <DataFrame>}`` – when the code
          sets a variable called ``result`` that is a DataFrame.
        * ``{"type": "text", "data": <str>}`` – when ``result`` is set to a
          non-DataFrame value **or** when stdout output was produced.
        * ``{"type": "image", "data": <path>}`` – when matplotlib figures
          were created (saved as a temporary PNG).
        * ``{"type": "error", "data": <str>}`` – on any exception.
    """
    # ---- build the restricted namespace ----
    namespace: Dict[str, Any] = {
        "df": df,
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
    }

    # ---- capture stdout ----
    old_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    # ---- timeout machinery ----
    timed_out = threading.Event()

    def _raise_timeout() -> None:
        timed_out.set()

    timer = threading.Timer(timeout, _raise_timeout)

    try:
        timer.start()

        exec(code, namespace)  # noqa: S102 – intentional exec

        if timed_out.is_set():
            return {
                "type": "error",
                "data": f"Execution timed out after {timeout} seconds.",
                "code": code,
            }

        # ---- determine result type ----

        # 1. Explicit `result` variable
        if "result" in namespace:
            result = namespace["result"]
            if isinstance(result, pd.DataFrame):
                return {"type": "dataframe", "data": result, "code": code}
            return {"type": "text", "data": str(result), "code": code}

        # 2. Matplotlib figures
        if plt.get_fignums():
            tmp = tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, prefix="analyst_plot_"
            )
            plt.savefig(tmp.name, bbox_inches="tight", dpi=150)
            tmp.close()
            return {"type": "image", "data": tmp.name, "code": code}

        # 3. Captured stdout
        stdout_content = captured_output.getvalue()
        if stdout_content.strip():
            return {"type": "text", "data": stdout_content, "code": code}

        # 4. Nothing produced
        return {"type": "text", "data": "Code executed successfully (no output).", "code": code}

    except Exception as exc:
        return {"type": "error", "data": str(exc), "code": code}

    finally:
        timer.cancel()
        sys.stdout = old_stdout
        # Clean up all matplotlib figures to free memory
        plt.close("all")
