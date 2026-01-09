"""
Base agent pattern for Brain OS.
All agents inherit from this class for consistency.

Usage:
    class MyAgent(BaseAgent):
        config = AgentConfig(
            name="my_agent",
            model="openrouter/creative",
            prompt_template="Process this: {input}",
            output_format="markdown"
        )

    result = await MyAgent.run(input_data="...")
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.utils.llm import get_groq_client, get_openrouter_client, get_groq_model, get_openrouter_model

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GROQ = "groq"
    OPENROUTER = "openrouter"


class OutputFormat(str, Enum):
    """Supported output formats."""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"


@dataclass(frozen=True)
class AgentConfig:
    """
    Configuration for an agent.

    Modify these values to change agent behavior without touching code.
    """

    name: str
    """Unique identifier for this agent."""

    model: str
    """Model identifier in format: 'provider/model-task' (e.g., 'openrouter/creative')"""

    prompt_template: str
    """Prompt template with {placeholders} for variable substitution."""

    output_format: OutputFormat = OutputFormat.MARKDOWN
    """How to structure the output."""

    temperature: float = 0.7
    """LLM temperature (0.0 = deterministic, 1.0 = creative)."""

    max_tokens: int = 2000
    """Maximum tokens in the response."""

    system_prompt: str | None = None
    """Optional system prompt to set context."""

    timeout_seconds: int = 30
    """Timeout for LLM requests."""


class BaseAgent(ABC):
    """
    Base class for all Brain OS agents.

    Provides configuration-driven execution with minimal code.
    Subclasses only need to define their `config` class attribute.
    """

    config: AgentConfig
    """Subclasses must override this with their configuration."""

    @classmethod
    def parse_model(cls, model_str: str) -> tuple[LLMProvider, str]:
        """
        Parse model string into provider and model task.

        Args:
            model_str: Model string like 'openrouter/creative' or 'groq/quick'

        Returns:
            Tuple of (LLMProvider, model_task)
        """
        try:
            provider_str, task = model_str.split("/", 1)
            provider = LLMProvider(provider_str.lower())
            return provider, task
        except ValueError:
            logger.warning(f"Invalid model format '{model_str}', defaulting to openrouter/creative")
            return LLMProvider.OPENROUTER, "creative"

    @classmethod
    def resolve_model(cls, provider: LLMProvider, task: str) -> str:
        """
        Resolve task to actual model name.

        Args:
            provider: LLM provider
            task: Model task (quick, creative, researching, planning)

        Returns:
            Actual model name to use.
        """
        if provider == LLMProvider.GROQ:
            return get_groq_model()
        else:  # OPENROUTER
            return get_openrouter_model(task)

    @classmethod
    async def run(cls, **variables: Any) -> str:
        """
        Execute the agent with the given variables.

        Args:
            **variables: Variables to substitute into prompt_template

        Returns:
            The LLM response as a string.
        """
        if not hasattr(cls, "config"):
            raise RuntimeError(f"Agent {cls.__name__} must define a 'config' class attribute")

        config = cls.config

        # Parse model configuration
        provider, task = cls.parse_model(config.model)
        model_name = cls.resolve_model(provider, task)

        # Build prompt by substituting variables
        try:
            prompt = config.prompt_template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable for prompt template: {e}")

        # Get appropriate client
        if provider == LLMProvider.GROQ:
            client = get_groq_client()
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
            return response.choices[0].message.content
        else:  # OPENROUTER
            client = get_openrouter_client()
            messages = []
            if config.system_prompt:
                messages.append({"role": "system", "content": config.system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
            return response.choices[0].message.content

    @classmethod
    def get_info(cls) -> dict[str, Any]:
        """
        Get agent configuration info.

        Returns:
            Dictionary with agent metadata.
        """
        if not hasattr(cls, "config"):
            return {"error": "Agent must define a 'config' class attribute"}

        config = cls.config
        provider, task = cls.parse_model(config.model)

        return {
            "name": config.name,
            "model": config.model,
            "provider": provider.value,
            "task": task,
            "output_format": config.output_format.value,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
