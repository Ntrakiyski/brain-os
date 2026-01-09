"""
Memory creation tool.
Stores new bubbles in the Synaptic Graph.
"""

import logging
from pydantic import Field

from src.database.queries.memory import upsert_bubble
from src.utils.schemas import BubbleCreate

logger = logging.getLogger(__name__)


def register_create_memory(mcp) -> None:
    """Register the create_memory tool with FastMCP."""

    @mcp.tool
    async def create_memory(
        content: str = Field(description="The information to remember"),
        sector: str = Field(
            description="Cognitive sector: Episodic, Semantic, Procedural, Emotional, or Reflective"
        ),
        source: str = Field(
            default="direct_chat",
            description="Origin of the data (e.g., transcript, direct_chat)",
        ),
        salience: float = Field(default=0.5, description="Importance score from 0.0 to 1.0"),
    ) -> str:
        """
        Store a new memory in the Synaptic Graph.

        Creates a Bubble node with automatic timestamp tracking.
        Use this to preserve important context across sessions.
        """
        try:
            # Validate and create the bubble
            bubble_data = BubbleCreate(
                content=content, sector=sector, source=source, salience=salience
            )
            result = await upsert_bubble(bubble_data)

            return (
                f"Memory stored successfully!\n"
                f"- ID: {result.id}\n"
                f"- Sector: {result.sector}\n"
                f"- Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"- Salience: {result.salience}\n"
                f"- Content: {result.content[:100]}{'...' if len(result.content) > 100 else ''}"
            )
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            return f"Error storing memory: {str(e)}"
