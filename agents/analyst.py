"""
Data Analyst agent definition.

The analyst interprets the user's question in the context of the data
profile and produces a clear, step-by-step analysis plan for the coder.
"""

from crewai import Agent, Task
from .config import get_model


def create_analyst_agent(api_key: str = None) -> Agent:
    """Create and return the Senior Data Analyst agent."""
    return Agent(
        role="Senior Data Analyst",
        goal=(
            "Analyze the user's question in context of the data profile and "
            "create a clear, actionable analysis plan."
        ),
        backstory=(
            "You are a seasoned data analyst with 15 years of experience. "
            "Given a question about a dataset, you determine the best "
            "analytical approach — whether it needs aggregation, filtering, "
            "visualization, statistical testing, or a combination."
        ),
        llm=get_model("analyst", api_key=api_key),
        verbose=True,
        allow_delegation=False,
    )


def create_analysis_task(agent: Agent, question: str, profile: str) -> Task:
    """Create an analysis-planning task.

    Args:
        agent: The analyst Agent instance.
        question: The user's natural-language question about the data.
        profile: The data profile produced by the profiler agent.

    Returns:
        A CrewAI Task that produces a step-by-step analysis plan.
    """
    return Task(
        description=(
            f"Given the user's question and the data profile below, create a "
            f"detailed, step-by-step analysis plan.\n\n"
            f"**User Question:** {question}\n\n"
            f"**Data Profile:**\n{profile}\n\n"
            f"Your plan MUST specify:\n"
            f"1. **Columns to Use** — which columns are relevant and why.\n"
            f"2. **Operations Needed** — filtering, grouping, aggregation, "
            f"pivoting, statistical tests, etc.\n"
            f"3. **Expected Output Type** — one of: chart, table, number, or text.\n"
            f"4. **Chart Type** (if applicable) — bar, line, scatter, histogram, "
            f"pie, heatmap, box, etc., with justification.\n"
            f"5. **Step-by-Step Instructions** — ordered list of operations "
            f"the code writer should implement."
        ),
        expected_output=(
            "A detailed, step-by-step analysis plan in Markdown specifying "
            "columns, operations, expected output type, chart type (if any), "
            "and ordered implementation steps."
        ),
        agent=agent,
    )
