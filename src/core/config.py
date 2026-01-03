"""
Core configuration for Brain OS.
Loads environment variables and provides global settings.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class Neo4jConfig:
    """Neo4j database configuration."""
    uri: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        return cls(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "brainos_password_123")
        )


@dataclass(frozen=True)
class GroqConfig:
    """Groq API configuration for fast actions."""
    api_key: str
    quick_model: str

    @classmethod
    def from_env(cls) -> "GroqConfig":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return cls(
            api_key=api_key,
            quick_model=os.getenv("GROQ_QUICK_MODEL", "openai/gpt-oss-120b")
        )


@dataclass(frozen=True)
class OpenRouterConfig:
    """OpenRouter API configuration for deep thinking."""
    api_key: str
    researching_model: str
    thinking_model: str
    creative_model: str
    planning_model: str

    @classmethod
    def from_env(cls) -> "OpenRouterConfig":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        return cls(
            api_key=api_key,
            researching_model=os.getenv("OPENROUTER_RESEARCHING_MODEL", "anthropic/claude-sonnet-4"),
            thinking_model=os.getenv("OPENROUTER_THINKINIG_MODEL", "anthropic/claude-sonnet-4"),
            creative_model=os.getenv("OPENROUTER_CREATIVE_MODEL", "anthropic/claude-sonnet-4"),
            planning_model=os.getenv("OPENROUTER_PLANNING_MODEL", "anthropic/claude-opus-4")
        )


# Global configuration instances
neo4j = Neo4jConfig.from_env()
groq = GroqConfig.from_env()
openrouter = OpenRouterConfig.from_env()


# Five-sector ontology constants
SECTOR_EPISODIC = "Episodic"
SECTOR_SEMANTIC = "Semantic"
SECTOR_PROCEDURAL = "Procedural"
SECTOR_EMOTIONAL = "Emotional"
SECTOR_REFLECTIVE = "Reflective"

VALID_SECTORS = {
    SECTOR_EPISODIC,
    SECTOR_SEMANTIC,
    SECTOR_PROCEDURAL,
    SECTOR_EMOTIONAL,
    SECTOR_REFLECTIVE,
}
