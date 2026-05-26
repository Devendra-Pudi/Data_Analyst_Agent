"""
Configuration module for AI Data Analyst agent models.

Manages OpenRouter API settings and model assignments for each agent role.
All models are free-tier OpenRouter models accessed via LiteLLM.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

AGENT_MODELS = {
    "profiler": "openrouter/google/gemma-4-31b-it:free",
    "analyst": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    "coder": "openrouter/qwen/qwen3-coder:free",
    "reporter": "openrouter/deepseek/deepseek-v4-flash:free",
}


def get_model(role: str) -> str:
    """Return the LiteLLM model identifier for the given agent role.

    Args:
        role: One of 'profiler', 'analyst', 'coder', or 'reporter'.

    Returns:
        The model string. Falls back to the coder model for unknown roles.
    """
    return AGENT_MODELS.get(role, AGENT_MODELS["coder"])
