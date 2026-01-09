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
            description="Natural language context (e.g., 'I'm starting work on Project A', 'Now deploying to production', 'Meeting with FastTrack client'). The system extracts concepts and auto-activates relevant memories."
        ),
    ) -> str:
        """
        Automatic memory activation based on context (The Oven Analogy).

        **This is different from get_memory**: Instead of explicit search, this
        tool surfaces instinctive knowledge automatically—like knowing the oven
        is hot without thinking about it.

        How It Works:
        1. Concept Extraction (~100ms): Groq analyzes input for key concepts
        2. Pattern Matching: Matches concepts against entities, content, observations
        3. Activation: Returns memories where activation_threshold < concept_salience

        When to Use This:
        ✓ Starting work on a project ("I'm starting work on Project A...")
        ✓ Switching contexts ("Now I'm on deployment...")
        ✓ Can't recall what you're forgetting
        ✓ Feeling like you're missing important context

        When NOT to Use This:
        ✗ You know what you're looking for (use get_memory)
        ✗ Need comprehensive overview (use get_all_memories)
        ✗ Complex query requiring synthesis (use get_memory_relations)

        What Gets Activated:
        Only memories marked with memory_type='instinctive' and low activation_threshold (0.2-0.3):
        - Technology stack choices
        - Pricing structures
        - Deployment procedures
        - Client preferences

        Real-World Examples:
        - "I'm deploying Project A" → Returns deployment procedures, stack choices
        - "Meeting with FastTrack" → Returns client history, pricing, preferences
        - "Building an API" → Returns framework choices, architecture decisions
        - "Database design needed" → Returns database decisions, SQL vs NoSQL rationale
        """
        try:
            # Run the instinctive activation flow
            shared = {
                "neo4j_driver": await get_driver(),
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
