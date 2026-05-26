"""
Report Writer agent definition.

The reporter transforms raw analysis results into a compelling,
non-technical narrative with key findings and follow-up suggestions.
"""

from crewai import Agent, Task
from .config import get_model


def create_reporter_agent() -> Agent:
    """Create and return the Senior Data Report Writer agent."""
    return Agent(
        role="Senior Data Report Writer",
        goal=(
            "Create clear, insightful narrative reports that explain analysis "
            "results to non-technical stakeholders."
        ),
        backstory=(
            "You are a data storyteller who transforms raw analysis results "
            "into compelling narratives. You highlight key findings, provide "
            "context, and suggest follow-up questions."
        ),
        llm=get_model("reporter"),
        verbose=True,
        allow_delegation=False,
    )


def create_report_task(
    agent: Agent, question: str, code: str, result_summary: str
) -> Task:
    """Create a report-writing task.

    Args:
        agent: The reporter Agent instance.
        question: The original user question.
        code: The Python code that was executed.
        result_summary: A textual summary of the execution results.

    Returns:
        A CrewAI Task that produces a Markdown report.
    """
    return Task(
        description=(
            f"Write a clear, insightful Markdown report based on the analysis "
            f"results below.\n\n"
            f"**Original Question:** {question}\n\n"
            f"**Code Executed:**\n```python\n{code}\n```\n\n"
            f"**Result Summary:**\n{result_summary}\n\n"
            f"Your report MUST include the following sections:\n"
            f"1. **Key Findings** — the most important takeaways, written in "
            f"plain language for non-technical readers.\n"
            f"2. **Detailed Analysis** — a deeper explanation of the results, "
            f"including any notable patterns, trends, or anomalies.\n"
            f"3. **Suggested Follow-up Questions** — 3-5 follow-up questions "
            f"that could deepen the analysis or uncover related insights."
        ),
        expected_output=(
            "A polished Markdown report with sections: Key Findings, "
            "Detailed Analysis, and Suggested Follow-up Questions."
        ),
        agent=agent,
    )
