"""
data_loader.py – Robust file-to-DataFrame loader for the AI Data Analyst.

Supports CSV, Excel (.xlsx/.xls), and JSON uploads via Streamlit's
UploadedFile interface.  Encoding and delimiter detection is handled
automatically so the caller never has to worry about it.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_data(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """Read a Streamlit UploadedFile and return a pandas DataFrame.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        The file object produced by ``st.file_uploader``.

    Returns
    -------
    pd.DataFrame
        Parsed tabular data.

    Raises
    ------
    ValueError
        If the file extension is not supported or the file cannot be parsed.
    """
    filename: str = uploaded_file.name
    extension: str = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""

    if extension == "csv":
        return _load_csv(uploaded_file)
    elif extension in ("xlsx", "xls"):
        return _load_excel(uploaded_file)
    elif extension == "json":
        return _load_json(uploaded_file)
    else:
        raise ValueError(
            f"Unsupported file type: '.{extension}'. "
            "Please upload a CSV, Excel (.xlsx/.xls), or JSON file."
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_csv(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """Try multiple encoding / delimiter combinations to read a CSV."""
    encodings = ["utf-8", "latin-1"]
    delimiters = [",", ";", "\t"]

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file,
                    encoding=encoding,
                    delimiter=delimiter,
                )
                # A successful parse with the wrong delimiter often yields a
                # single-column DataFrame.  Accept it only if we got more than
                # one column **or** the file genuinely has just one column
                # (i.e. it also has only one column with the first delimiter).
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue

    # If every multi-column attempt failed, fall back to the very first
    # successful single-column parse (utf-8 + comma).
    try:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="utf-8", delimiter=",")
    except Exception:
        pass

    try:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="latin-1", delimiter=",")
    except Exception as exc:
        raise ValueError(
            f"Failed to parse CSV file '{uploaded_file.name}'. "
            f"Last error: {exc}"
        ) from exc


def _load_excel(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """Read an Excel file using the openpyxl engine."""
    try:
        uploaded_file.seek(0)
        return pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as exc:
        raise ValueError(
            f"Failed to parse Excel file '{uploaded_file.name}'. "
            f"Error: {exc}"
        ) from exc


def _load_json(uploaded_file: "UploadedFile") -> pd.DataFrame:
    """Read a JSON file, trying both 'records' and 'columns' orientations."""
    raw_bytes: bytes = uploaded_file.read()
    uploaded_file.seek(0)

    # Try default (records / list-of-dicts) first
    try:
        return pd.read_json(io.BytesIO(raw_bytes))
    except Exception:
        pass

    # Try columnar orientation
    try:
        return pd.read_json(io.BytesIO(raw_bytes), orient="columns")
    except Exception:
        pass

    # Try records orientation explicitly
    try:
        return pd.read_json(io.BytesIO(raw_bytes), orient="records")
    except Exception as exc:
        raise ValueError(
            f"Failed to parse JSON file '{uploaded_file.name}'. "
            f"Error: {exc}"
        ) from exc
