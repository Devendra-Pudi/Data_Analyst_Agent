"""
Data Profiler agent definition.

The profiler examines a dataset's structure, types, missing values, and
basic statistics to produce a comprehensive data profile that downstream
agents use as context.
"""

from crewai import Agent, Task
from .config import get_model


def create_profiler_agent(api_key: str = None) -> Agent:
    """Create and return the Senior Data Profiler agent."""
    return Agent(
        role="Senior Data Profiler",
        goal=(
            "Analyze the dataset structure, data types, missing values, "
            "and basic statistics to create a comprehensive data profile."
        ),
        backstory=(
            "You are an expert data scientist who specializes in understanding "
            "datasets at a glance. You identify data types, patterns, anomalies, "
            "and key statistics that help analysts understand what they're "
            "working with."
        ),
        llm=get_model("profiler", api_key=api_key),
        verbose=True,
        allow_delegation=False,
    )


def create_profile_task(agent: Agent, data_summary: str) -> Task:
    """Create a profiling task for the given agent.

    Args:
        agent: The profiler Agent instance.
        data_summary: A text summary of the DataFrame including head,
            dtypes, describe output, shape, columns, and null counts.

    Returns:
        A CrewAI Task that produces a structured data profile.
    """
    return Task(
        description=(
            f"Analyze the following dataset summary and produce a structured "
            f"data profile.\n\n"
            f"Dataset Summary:\n{data_summary}\n\n"
            f"Your profile MUST include:\n"
            f"1. **Overview** — number of rows, columns, and memory considerations.\n"
            f"2. **Column Analysis** — for each column: data type, number of unique "
            f"values, missing value count/percentage, and sample values.\n"
            f"3. **Numeric Statistics** — min, max, mean, median, std dev for "
            f"numeric columns.\n"
            f"4. **Data Quality Issues** — missing data patterns, potential outliers, "
            f"inconsistent formats.\n"
            f"5. **Initial Observations** — notable patterns, relationships between "
            f"columns, or potential areas of interest."
        ),
        expected_output=(
            "A structured Markdown data profile covering overview, column analysis, "
            "numeric statistics, data quality issues, and initial observations."
        ),
        agent=agent,
    )
