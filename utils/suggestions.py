"""Smart suggestion engine that analyzes a DataFrame and generates relevant analysis prompts."""

from __future__ import annotations

import pandas as pd


def generate_suggestions(df: pd.DataFrame) -> list[str]:
    """Analyze *df* and return 5-10 actionable analysis prompts.

    The suggestions are context-aware – they adapt to the column types,
    cardinality, and shape of the data so the user always sees relevant
    starting points for exploration.
    """

    suggestions: list[str] = []

    # ── Classify columns ────────────────────────────────────────────
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()

    # Also try to detect datetime-like object columns
    for col in categorical_cols[:]:
        try:
            pd.to_datetime(df[col], format="mixed", errors="raise")
            datetime_cols.append(col)
            categorical_cols.remove(col)
        except (ValueError, TypeError, OverflowError):
            pass

    # ── Numeric column suggestions ──────────────────────────────────
    for col in numeric_cols:
        suggestions.append(
            f"Show the distribution / histogram of '{col}'"
        )
        if len(suggestions) >= 10:
            break

    # Correlation heatmap when 2+ numeric columns exist
    if len(numeric_cols) >= 2:
        suggestions.append(
            "Plot a correlation heatmap of all numeric columns"
        )

    # ── Categorical column suggestions ──────────────────────────────
    low_cardinality_cats = [
        c for c in categorical_cols if df[c].nunique() < 20
    ]
    for col in low_cardinality_cats:
        suggestions.append(
            f"Show a value-counts bar chart for '{col}'"
        )
        if len(suggestions) >= 10:
            break

    # ── Datetime suggestions ────────────────────────────────────────
    if datetime_cols:
        dt_col = datetime_cols[0]
        if numeric_cols:
            suggestions.append(
                f"Plot a time-series of '{numeric_cols[0]}' over '{dt_col}'"
            )
        else:
            suggestions.append(
                f"Show the record count over time using '{dt_col}'"
            )

    # ── Cross-type suggestions ──────────────────────────────────────
    if numeric_cols and categorical_cols:
        cat = low_cardinality_cats[0] if low_cardinality_cats else categorical_cols[0]
        num = numeric_cols[0]
        suggestions.append(
            f"Show a group-by analysis of '{num}' grouped by '{cat}'"
        )

    # ── Universal suggestions (always present) ──────────────────────
    suggestions.append("Show basic statistics summary")
    suggestions.append("Show missing data analysis")

    # ── De-duplicate while preserving order, then cap at 10 ─────────
    seen: set[str] = set()
    unique: list[str] = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique.append(s)

    return unique[:10]
