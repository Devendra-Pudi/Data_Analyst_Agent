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
    """Execute *code* against a DataFrame in a subprocess and return structured output.

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
    import os
    import sys
    import tempfile
    import subprocess
    import pickle
    import uuid

    # Create temporary files for communication
    temp_dir = tempfile.gettempdir()
    run_id = str(uuid.uuid4())

    input_df_path = os.path.join(temp_dir, f"df_input_{run_id}.pkl")
    output_res_path = os.path.join(temp_dir, f"res_output_{run_id}.pkl")
    output_img_path = os.path.join(temp_dir, f"img_output_{run_id}.png")
    script_path = os.path.join(temp_dir, f"run_script_{run_id}.py")

    try:
        # Save the input DataFrame
        df.to_pickle(input_df_path)

        # Build the python script content
        script_lines = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "import sys",
            "",
            "# Load the pre-loaded DataFrame",
            "df = pd.read_pickle(sys.argv[1])",
            "",
            "# Bind common library references to local/global scope",
            "pd = pd",
            "np = np",
            "plt = plt",
            "sns = sns",
            "",
            "# --- USER CODE START ---",
            code,
            "# --- USER CODE END ---",
            "",
            "# Save result variable if created",
            "import pickle",
            "if 'result' in locals() or 'result' in globals():",
            "    val = locals().get('result', globals().get('result'))",
            "    with open(sys.argv[2], 'wb') as f:",
            "        pickle.dump(val, f)",
            "",
            "# Save chart if figure exists",
            "if plt.get_fignums():",
            "    plt.savefig(sys.argv[3], bbox_inches='tight', dpi=150)",
            "    plt.close('all')"
        ]

        script_content = "\n".join(script_lines)

        # Write script to temporary file using UTF-8 encoding
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Execute the python script in a subprocess using the same python interpreter
        process = subprocess.run(
            [sys.executable, script_path, input_df_path, output_res_path, output_img_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8"
        )

        # Check for execution error
        if process.returncode != 0:
            error_msg = process.stderr.strip() or process.stdout.strip() or "Unknown execution error."
            # Remove wrapper script paths from traceback for readability
            clean_error = []
            for line in error_msg.splitlines():
                if "run_script_" not in line:
                    clean_error.append(line)
            return {
                "type": "error",
                "data": "\n".join(clean_error) or error_msg,
                "code": code
            }

        # Check if result variable was serialized
        if os.path.exists(output_res_path):
            with open(output_res_path, "rb") as f:
                result = pickle.load(f)
            if isinstance(result, pd.DataFrame):
                return {"type": "dataframe", "data": result, "code": code}
            return {"type": "text", "data": str(result), "code": code}

        # Check if an image was generated
        if os.path.exists(output_img_path):
            persistent_img_path = os.path.join(temp_dir, f"analyst_plot_{run_id}.png")
            os.rename(output_img_path, persistent_img_path)
            return {"type": "image", "data": persistent_img_path, "code": code}

        # Check for stdout
        stdout_content = process.stdout.strip()
        if stdout_content:
            return {"type": "text", "data": stdout_content, "code": code}

        return {"type": "text", "data": "Code executed successfully (no output).", "code": code}

    except subprocess.TimeoutExpired:
        return {
            "type": "error",
            "data": f"Execution timed out after {timeout} seconds.",
            "code": code
        }
    except Exception as exc:
        return {
            "type": "error",
            "data": f"{type(exc).__name__}: {exc}",
            "code": code
        }
    finally:
        # Clean up temporary files
        for path in [input_df_path, output_res_path, output_img_path, script_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
