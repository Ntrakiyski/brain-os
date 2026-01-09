"""
Memory retrieval tools.
Fetches bubbles from the Synaptic Graph.
"""

import logging
from pydantic import Field

from src.database.queries.memory import search_bubbles, get_all_bubbles

logger = logging.getLogger(__name__)


def register_get_memory(mcp) -> None:
    """Register the memory retrieval tools with FastMCP."""

    @mcp.tool
    async def get_memory(
        query: str = Field(description="The search term to find matching memories"),
        limit: int = Field(default=10, description="Maximum number of results to return"),
    ) -> str:
        """
        Retrieve memories from the Synaptic Graph based on a keyword search.

        Returns bubbles matching the query, ordered by recency.
        Use this to recall previously stored context.
        """
        try:
            results = await search_bubbles(query, limit)

            if not results:
                return f"No memories found matching query: '{query}'"

            output = [f"Found {len(results)} memories matching '{query}':\n"]
            for i, bubble in enumerate(results, 1):
                output.append(
                    f"\n{i}. ID: {bubble.id} | Sector: {bubble.sector} | "
                    f"Salience: {bubble.salience:.2f}\n"
                    f"   Created: {bubble.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                    f"   Source: {bubble.source}\n"
                    f"   Content: {bubble.content}"
                )

            return "\n".join(output)
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
            return f"Error retrieving memory: {str(e)}"

    @mcp.tool
    async def get_all_memories(
        limit: int = Field(
            default=50, description="Maximum number of memories to return", ge=1, le=200
        ),
    ) -> str:
        """
        Retrieve all memories from the Synaptic Graph.

        Returns all active bubbles ordered by recency (most recent first).
        Use this to get a complete overview of stored memories.
        """
        try:
            results = await get_all_bubbles(limit)

            if not results:
                return "No memories stored yet. Use create_memory to store your first memory."

            # Group by sector for summary
            sector_counts = {}
            for bubble in results:
                sector_counts[bubble.sector] = sector_counts.get(bubble.sector, 0) + 1

            output = [
                f"[STATS] Total Memories: {len(results)}\n",
                f"[SECTORS] Sector Distribution:\n",
            ]
            for sector, count in sorted(sector_counts.items()):
                percentage = (count / len(results)) * 100
                bar = "#" * int(percentage / 5)
                output.append(f"  {sector:12} | {bar} {count} ({percentage:.1f}%)\n")

            output.append(f"\n{'-' * 60}\n")
            output.append("Recent Memories:\n\n")

            for i, bubble in enumerate(results, 1):
                output.append(
                    f"{i}. [{bubble.sector}] Salience: {bubble.salience:.2f}\n"
                    f"   Created: {bubble.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"   Content: {bubble.content[:100]}{'...' if len(bubble.content) > 100 else ''}\n"
                )

            return "\n".join(output)
        except Exception as e:
            logger.error(f"Failed to retrieve all memories: {e}")
            return f"Error retrieving memories: {str(e)}"
