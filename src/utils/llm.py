"""
LLM client factory for Brain OS.
Provides Groq (System 1 - fast) and OpenRouter (System 2 - deep) clients.

Usage:
    from src.utils.llm import get_groq_client, get_openrouter_client

    # Fast classification (~100ms)
    groq = get_groq_client()
    response = groq.chat.completions.create(...)

    # Deep thinking (~3-10s)
    openrouter = get_openrouter_client()
    response = await openrouter.chat.completions.create(...)
"""

import os
from dataclasses import dataclass
from functools import lru_cache

import groq
from openai import AsyncOpenAI


@dataclass(frozen=True)
class GroqConfig:
    """Groq configuration for System 1 (fast) thinking."""

    api_key: str
    quick_model: str

    @classmethod
    def from_env(cls) -> "GroqConfig":
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("GROQ_API_KEY", ""),
            quick_model=os.getenv("GROG_QUICK_MODEL", "openai/gpt-oss-120b"),
        )


@dataclass(frozen=True)
class OpenRouterConfig:
    """OpenRouter configuration for System 2 (deep) thinking."""

    api_key: str
    researching_model: str
    creative_model: str
    planning_model: str

    @classmethod
    def from_env(cls) -> "OpenRouterConfig":
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            researching_model=os.getenv("OPENROUTER_RESEARCHING_MODEL", "anthropic/claude-sonnet-4"),
            creative_model=os.getenv("OPENROUTER_CREATIVE_MODEL", "anthropic/claude-sonnet-4"),
            planning_model=os.getenv("OPENROUTER_PLANNING_MODEL", "anthropic/claude-opus-4"),
        )


@lru_cache(maxsize=1)
def get_groq_client() -> groq.Groq:
    """
    Get a cached Groq client for fast LLM operations.

    Use for: Classification, extraction, routing, sentiment analysis.
    Speed: ~100-200ms per request.
    Cost: ~$0.10 per 1M tokens.

    Returns:
        Groq client instance.
    """
    config = GroqConfig.from_env()
    if not config.api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return groq.Groq(api_key=config.api_key)


@lru_cache(maxsize=1)
def get_openrouter_client() -> AsyncOpenAI:
    """
    Get a cached OpenRouter client for deep LLM operations.

    Use for: Research, synthesis, creative writing, planning.
    Speed: ~3-10s per request.
    Cost: ~$1-15 per 1M tokens (depending on model).

    Returns:
        AsyncOpenAI client instance configured for OpenRouter.
    """
    config = OpenRouterConfig.from_env()
    if not config.api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")
    return AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=config.api_key,
    )


def get_groq_model() -> str:
    """Get the configured Groq model name."""
    return GroqConfig.from_env().quick_model


def get_openrouter_model(task: str = "creative") -> str:
    """
    Get the configured OpenRouter model for a specific task.

    Args:
        task: Task type - "researching", "creative", or "planning"

    Returns:
        Model name string.
    """
    config = OpenRouterConfig.from_env()
    models = {
        "researching": config.researching_model,
        "creative": config.creative_model,
        "planning": config.planning_model,
    }
    return models.get(task, config.creative_model)
