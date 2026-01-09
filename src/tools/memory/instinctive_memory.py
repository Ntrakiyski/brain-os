"""
Instinctive Memory Tool.
MCP tool wrapper for the instinctive_activation PocketFlow.
"""

import logging

from pydantic import Field

from src.database.connection import get_driver
from src.flows.instinctive_activation import instinctive_activation_flow

logger = logging.getLogger(__name__)


def register_instinctive_memory(mcp) -> None:
    """Register the get_instinctive_memory tool with FastMCP."""

    @mcp.tool
    async def get_instinctive_memory(
        user_input: str = Field(
            description="User's message to analyze for automatic memory activation"
        ),
    ) -> str:
        """
        Retrieve memories that automatically activate based on input.

        Unlike get_memory (explicit search), this tool surfaces instinctive
        knowledge without conscious search—like knowing the oven is hot
        without thinking about it.

        This tool:
        1. Analyzes input for concept triggers (fast Groq classification ~100ms)
        2. Finds memories with low activation_threshold matching concepts
        3. Returns instinctive memories organized by theme

        **Instinctive memories** are those marked with memory_type='instinctive',
        which have low activation_threshold (0.2-0.3) and automatically surface
        when relevant concepts are detected.

        Use this when you want automatic knowledge activation, not explicit search.
        Use get_memory for simple, direct searches.

        **Example**:
            Input: "I'm starting work on Project A again"
            Output: Automatically surfaces instinctive memories like:
            - "Project A uses FastAPI, React + TypeScript, PostgreSQL, Redis"
            - "PostgreSQL chosen for ACID transaction compliance"
            - "Redis handles session caching with 30-minute TTL"
        """
        try:
            # Run the instinctive activation flow
            shared = {
                "neo4j_driver": get_driver(),
                "user_input": user_input
            }

            await instinctive_activation_flow.run_async(shared)

            memories = shared.get("instinctive_memories", [])

            if not memories:
                return f"No instinctive memories activated for: \"{user_input}\"\n\nTry using get_memory for explicit search, or create some instinctive memories first with create_memory(memory_type='instinctive')."

            # Group memories by sector for better organization
            by_sector = {}
            for memory in memories:
                sector = memory.sector or "General"
                if sector not in by_sector:
                    by_sector[sector] = []
                by_sector[sector].append(memory)

            # Format output
            output = [
                f"**{len(memories)} Instinctive Memories Activated**\n",
                f"Input: \"{user_input}\"\n\n"
            ]

            for sector, sector_memories in sorted(by_sector.items()):
                output.append(f"### {sector}\n")
                for memory in sector_memories:
                    # Format memory with metadata
                    meta_parts = []
                    if memory.salience:
                        meta_parts.append(f"Salience: {memory.salience:.2f}")
                    if memory.accessed_count:
                        meta_parts.append(f"Accessed: {memory.accessed_count}x")

                    meta_str = f" ({', '.join(meta_parts)})" if meta_parts else ""
                    output.append(f"- {memory.content}{meta_str}\n")

                output.append("\n")

            return "".join(output)

        except Exception as e:
            logger.error(f"Failed to activate instinctive memories: {e}", exc_info=True)
            return f"Error activating instinctive memories: {str(e)}"
