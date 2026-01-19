"""
Update memory observations tool.
Updates observations on an existing memory in Neo4j.

Phase 2 Sync: Used by Obsidian sync to update Neo4j with observations
edited in Obsidian markdown files.
"""

import logging
from pydantic import Field

from src.database.queries.memory import update_bubble_observations
from src.utils.observability import instrument_mcp_tool

logger = logging.getLogger(__name__)


def register_update_memory_observations(mcp) -> None:
    """Register the update_memory_observations tool with FastMCP."""

    @mcp.tool
    @instrument_mcp_tool("update_memory_observations")
    async def update_memory_observations(
        memory_id: str = Field(
            description="The numeric Neo4j ID of the memory to update"
        ),
        observations: list[str] = Field(
            description="Updated observations list"
        ),
        append: bool = Field(
            default=False,
            description="If True, append to existing observations (avoiding duplicates). If False, replace all observations."
        ),
    ) -> str:
        """
        Update observations on an existing memory in Neo4j.

        **Use this to sync observations edited in Obsidian back to Neo4j.**

        Common Patterns:

        **Replace observations** (default):
        - Observations list will completely replace existing observations
        - Use when full sync from Obsidian is needed

        **Append observations** (append=True):
        - New observations are added to existing ones
        - Duplicates are automatically filtered
        - Use when adding incremental updates

        Examples:
        - Replace: observations=["New observation 1", "New observation 2"]
        - Append: observations=["Additional note"], append=True
        """
        try:
            logger.debug(f"update_memory_observations: Updating memory {memory_id}")

            result = await update_bubble_observations(
                bubble_id=memory_id,
                observations=observations,
                append=append
            )

            if result:
                mode = "appended to" if append else "updated"
                return (
                    f"Memory observations {mode} successfully!\n"
                    f"- Neo4j ID: {result.id}\n"
                    f"- Content: {result.content[:50]}{'...' if len(result.content) > 50 else ''}\n"
                    f"- Total observations: {len(result.observations)}"
                )
            else:
                return f"Error: Memory {memory_id} not found or update failed"

        except Exception as e:
            logger.error(f"Failed to update memory observations: {e}")
            return f"Error updating memory observations: {str(e)}"
