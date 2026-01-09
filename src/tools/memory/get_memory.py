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
        query: str = Field(
            description="Search term for finding memories (e.g., 'PostgreSQL', 'deployment', 'FastTrack pricing'). Case-insensitive keyword search."
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=200,
            description="Maximum results (1-200). Use 5-10 for specific lookups, 20-50 for broader searches"
        ),
    ) -> str:
        """
        Quick keyword search for memories.

        **Use this when you know what you're looking for.**

        Simple, fast keyword search that returns memories containing your
        search term. Case-insensitive, searches content and entities.

        When to Use This:
        ✓ Quick fact-checking ("What was the pricing?")
        ✓ Finding specific memories ("When did I meet with X?")
        ✓ Retrieving known information ("Deployment procedure")

        When NOT to Use This:
        ✗ Complex queries requiring synthesis (use get_memory_relations)
        ✗ Starting work on a project (use get_instinctive_memory)
        ✗ Need overview of everything (use get_all_memories)

        Output:
        - Returns memories matching your query
        - Ordered by recency (newest first)
        - Shows sector, salience, created date, source
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
            default=50,
            ge=1,
            le=200,
            description="Maximum memories to return (1-200). Use 20-50 for recent overview, 100+ for comprehensive review"
        ),
    ) -> str:
        """
        Complete overview with statistics and sector distribution.

        **Use this for starting work, weekly reviews, or feeling overwhelmed.**

        This tool provides:
        - Total memory count
        - Sector distribution with percentages
        - Visual ASCII bar chart
        - Recent memories list

        When to Use This:
        ✓ Starting work on a project (get context)
        ✓ Weekly reviews (see patterns)
        ✓ Feeling overwhelmed (ground yourself)
        ✓ Before planning sessions (inform decisions)

        When NOT to Use This:
        ✗ Looking for something specific (use get_memory)
        ✗ Need sector breakdown only (use list_sectors)
        ✗ Quick fact check (use get_memory)

        Cognitive Balance:
        After running this, check if your sector distribution is balanced:
        - Procedural: 20-30%, Semantic: 25-35%, Episodic: 15-25%
        - Emotional: 5-15%, Reflective: 5-15%

        If imbalanced, consider creating memories in underrepresented sectors.
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
