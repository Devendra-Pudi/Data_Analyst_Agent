"""
Code Writer agent definition.

The coder translates an analysis plan into clean, executable Python code
that uses pandas, matplotlib, and seaborn against a pre-loaded DataFrame.
"""

from crewai import Agent, Task
from .config import get_model


def create_coder_agent() -> Agent:
    """Create and return the Senior Python Developer agent."""
    return Agent(
        role="Senior Python Developer",
        goal=(
            "Write clean, correct, well-commented Python code that implements "
            "the analysis plan using pandas, matplotlib, and seaborn."
        ),
        backstory=(
            "You are an expert Python developer who writes data analysis code. "
            "You use pandas for data manipulation, matplotlib and seaborn for "
            "visualization. Your code is always well-commented so humans can "
            "understand and verify it."
        ),
        llm=get_model("coder"),
        verbose=True,
        allow_delegation=False,
    )


def create_code_task(agent: Agent, plan: str, columns_info: str) -> Task:
    """Create a code-writing task.

    Args:
        agent: The coder Agent instance.
        plan: The step-by-step analysis plan from the analyst.
        columns_info: Column names and dtypes for reference.

    Returns:
        A CrewAI Task that produces executable Python code.
    """
    return Task(
        description=(
            f"Implement the following analysis plan as Python code.\n\n"
            f"**Analysis Plan:**\n{plan}\n\n"
            f"**Available Columns:**\n{columns_info}\n\n"
            f"**CRITICAL RULES — you MUST follow all of these:**\n"
            f"1. Return your code inside a single ```python``` fenced block.\n"
            f"2. The DataFrame is already loaded as `df`. Do NOT read any files.\n"
            f"3. These are already imported and available — do NOT import them:\n"
            f"   - `pandas` as `pd`\n"
            f"   - `numpy` as `np`\n"
            f"   - `matplotlib.pyplot` as `plt`\n"
            f"   - `seaborn` as `sns`\n"
            f"4. For **table / numeric / text results**: assign the final answer "
            f"to a variable named `result` (must be a DataFrame or a string).\n"
            f"5. For **chart results**: create matplotlib/seaborn figures but "
            f"do **NOT** call `plt.show()`.\n"
            f"6. Add descriptive comments explaining each step.\n"
            f"7. Handle potential errors gracefully (e.g., missing columns, "
            f"empty DataFrames).\n"
            f"8. Do NOT use any libraries beyond pandas, numpy, matplotlib, "
            f"and seaborn."
        ),
        expected_output=(
            "A single Python code block (```python ... ```) containing clean, "
            "well-commented code that follows all the rules above. The code "
            "must either assign a `result` variable or create a chart."
        ),
        agent=agent,
    )
