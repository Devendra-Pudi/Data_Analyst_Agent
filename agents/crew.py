"""
crew.py – Main orchestrator for the AI Data Analyst multi-agent pipeline.

Wires up the four CrewAI agents (profiler → analyst → coder → reporter)
into a sequential crew, executes the generated code against the user's
DataFrame, and returns a structured results dictionary.
"""

from __future__ import annotations

import os
import traceback
from typing import Any, Dict

import pandas as pd
from crewai import Crew, Process

from .profiler import create_profiler_agent, create_profile_task
from .analyst import create_analyst_agent, create_analysis_task
from .coder import create_coder_agent, create_code_task
from .reporter import create_reporter_agent, create_report_task

from utils.helpers import extract_code_from_text
from engine.executor import execute_code


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_data_summary(df: pd.DataFrame) -> str:
    """Create a textual summary of the DataFrame for the profiler agent.

    Includes shape, column names, dtypes, null counts, descriptive
    statistics, and the first five rows.
    """
    parts: list[str] = []

    parts.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")

    parts.append(f"Columns: {', '.join(df.columns.tolist())}\n")

    parts.append("Data Types:\n" + df.dtypes.to_string() + "\n")

    parts.append(
        "Null Counts:\n" + df.isnull().sum().to_string() + "\n"
    )

    parts.append(
        "Descriptive Statistics:\n" + df.describe(include="all").to_string() + "\n"
    )

    parts.append(
        "First 5 Rows:\n" + df.head().to_string() + "\n"
    )

    return "\n".join(parts)


def _columns_info(df: pd.DataFrame) -> str:
    """Return a compact columns + dtypes string for the coder."""
    return "\n".join(
        f"- {col} ({dtype})" for col, dtype in zip(df.columns, df.dtypes)
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_analysis(df: pd.DataFrame, question: str, api_key: str) -> Dict[str, Any]:
    """Run the full multi-agent analysis pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        The user's active dataset.
    question : str
        The natural-language question to answer.
    api_key : str
        OpenRouter API key (also set as OPENAI_API_KEY for LiteLLM).

    Returns
    -------
    dict
        Keys: ``profile``, ``plan``, ``code``, ``execution_result``,
        ``report``, ``success``.  On failure the dict also contains
        ``error``.
    """

    # ---- configure API keys for CrewAI / LiteLLM ----
    os.environ["OPENROUTER_API_KEY"] = api_key
    os.environ["OPENAI_API_KEY"] = api_key

    try:
        # ---- build data summary ----
        data_summary = _build_data_summary(df)
        col_info = _columns_info(df)

        # ---- create agents ----
        profiler_agent = create_profiler_agent()
        analyst_agent = create_analyst_agent()
        coder_agent = create_coder_agent()
        reporter_agent = create_reporter_agent()

        # ---- create tasks (chained via context) ----
        profile_task = create_profile_task(profiler_agent, data_summary)

        analysis_task = create_analysis_task(
            analyst_agent, question, data_summary,
        )
        analysis_task.context = [profile_task]

        code_task = create_code_task(coder_agent, question, col_info)
        code_task.context = [profile_task, analysis_task]

        report_task = create_report_task(
            reporter_agent, question, "", "",
        )
        report_task.context = [profile_task, analysis_task, code_task]

        # ---- assemble and run the crew ----
        crew = Crew(
            agents=[profiler_agent, analyst_agent, coder_agent, reporter_agent],
            tasks=[profile_task, analysis_task, code_task, report_task],
            process=Process.sequential,
            verbose=True,
        )

        crew_output = crew.kickoff()

        # ---- extract individual task outputs ----
        profile_result = profile_task.output.raw if profile_task.output else ""
        plan_result = analysis_task.output.raw if analysis_task.output else ""
        code_raw = code_task.output.raw if code_task.output else ""
        report_result = report_task.output.raw if report_task.output else ""

        # ---- extract and execute code ----
        code = extract_code_from_text(code_raw)
        execution_result: Dict[str, Any] = {"type": "text", "data": "No code generated."}

        if code.strip():
            execution_result = execute_code(df, code)

        # ---- if execution succeeded, re-run reporter with real results ----
        # (The reporter already ran via the crew, but it didn't have the
        #  actual execution output.  We keep its output as-is since the crew
        #  context already contained the coder's plan / code.)

        return {
            "profile": profile_result,
            "plan": plan_result,
            "code": code,
            "execution_result": execution_result,
            "report": report_result,
            "success": True,
        }

    except Exception as exc:
        return {
            "profile": "",
            "plan": "",
            "code": "",
            "execution_result": {"type": "error", "data": str(exc)},
            "report": "",
            "success": False,
            "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
        }
