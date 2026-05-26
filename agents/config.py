"""
Configuration module for AI Data Analyst agent models.

Manages OpenRouter API settings and model assignments for each agent role.
All models are free-tier OpenRouter models accessed via LiteLLM.
"""

import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

AGENT_MODELS = {
    "profiler": "openrouter/arcee-ai/trinity-large-thinking:free",
    "analyst": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    "coder": "openrouter/poolside/laguna-m.1:free",
    "reporter": "openrouter/openai/gpt-oss-120b:free",
}


def get_model(role: str, api_key: str = None) -> LLM:
    """Return the CrewAI LLM instance for the given agent role.

    Args:
        role: One of 'profiler', 'analyst', 'coder', or 'reporter'.
        api_key: The OpenRouter API key.

    Returns:
        The LLM instance. Falls back to the coder model for unknown roles.
    """
    model_id = AGENT_MODELS.get(role, AGENT_MODELS["coder"])
    final_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
    
    return LLM(
        model=model_id,
        api_key=final_key,
        base_url="https://openrouter.ai/api/v1"
    )
