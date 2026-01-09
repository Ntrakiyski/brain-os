"""
Memory Relations Tool.
MCP tool wrapper for the contextual_retrieval PocketFlow.
"""

import logging
from typing import List

from pydantic import Field

from src.database.connection import get_driver
from src.flows.contextual_retrieval import contextual_retrieval_flow

logger = logging.getLogger(__name__)


def register_get_memory_relations(mcp) -> None:
    """Register the get_memory_relations tool with FastMCP."""

    @mcp.tool
    async def get_memory_relations(
        query: str = Field(
            description="What you're looking for. Be specific and conversational (e.g., 'Why did I choose PostgreSQL?', 'How do I deploy this project?', 'What are the key decisions for FastTrack?')"
        ),
        conversation_history: List[str] = Field(
            default=[],
            description="CRITICAL for context: Recent messages (last 5-10). Example: ['Building real-time notification system', 'Expected load: 1M messages/day', 'Budget constrained']"
        ),
        time_scope: str = Field(
            default="auto",
            description="Time filter: 'recent' (last 30 days), 'all_time' (everything), or 'auto' (let AI decide based on query)"
        ),
        salience_filter: str = Field(
            default="auto",
            description="Salience filter: 'high' (>0.6, important memories), 'any' (everything), or 'auto' (let AI decide based on query)"
        ),
    ) -> str:
        """
        Deep contextual retrieval with 3-agent synthesis system.

        **This is different from get_memory**: Instead of simple keyword search,
        this tool uses a 3-agent system for comprehensive understanding.

        The 3-Agent System:
        1. **Pre-Query Agent** (~100ms): Analyzes query + conversation history,
           extracts related concepts, determines optimal filters
        2. **Query Agent**: Searches Neo4j with expanded context, retrieves
           memories and their connections
        3. **Post-Query Agent** (~2-5s): Groups by theme, identifies insights,
           extracts relationships, generates synthesis

        When to Use This:
        ✓ "Why did I choose X over Y?" (Decision rationale)
        ✓ "How do I deploy this?" (All related memories)
        ✓ "What are the key decisions?" (High-level overview)
        ✓ Complex queries requiring synthesis
        ✓ Questions with context ("Given I'm building X, should I use Y?")

        When NOT to Use This:
        ✗ Simple keyword search (use get_memory)
        ✗ Quick lookup (faster tools available)
        ✗ Just need recent memories (use time filters elsewhere)

        Best Practices:
        1. ALWAYS provide conversation_history if available
        2. Be conversational in your query
        3. Review the synthesis (themes, insights, relationships)
        4. Use for understanding patterns, not fact-checking

        Output Sections:
        - Themes: What clusters emerged
        - Key Insights: Relevance explained
        - Relationships: How memories connect
        - All Memories: Reference list
        """
        try:
            # Run the contextual retrieval flow
            shared = {
                "neo4j_driver": await get_driver(),
                "user_input": query,
                "conversation_history": conversation_history,
                "time_scope": time_scope,
                "salience_filter": salience_filter
            }

            await contextual_retrieval_flow.run_async(shared)

            synthesis = shared.get("synthesis", {})

            if not synthesis or not synthesis.get("bubbles"):
                return f"""# Deep Memory Retrieval: {query}

No memories found.

**Suggestions**:
- Try a different search term
- Use get_memory for a simpler search
- Create some memories first with create_memory
"""

            bubbles = synthesis.get("bubbles", [])

            # Format output
            output = [
                f"# Deep Memory Retrieval: {query}\n",
                f"**Found {len(bubbles)} memories**\n",
                f"**Context**: {synthesis.get('intent', 'search')}\n"
            ]

            # Themes section
            if synthesis.get("themes"):
                output.append("\n## Themes\n")
                for theme in synthesis["themes"]:
                    relevance = theme.get("relevance", "medium")
                    name = theme.get("name", "Unknown")
                    output.append(f"\n### {name} ({relevance} relevance)\n")

            # Key insights section
            if synthesis.get("highlights"):
                output.append("\n## Key Insights\n")
                for highlight in synthesis["highlights"]:
                    content = highlight.get("content", "")
                    relevance = highlight.get("relevance", "")
                    output.append(f"\n- **{content}**\n  *{relevance}*\n")

            # Relationships section
            if synthesis.get("relationships"):
                output.append("\n## Relationships\n")
                for rel in synthesis["relationships"][:10]:
                    from_str = rel.get("from", "")
                    to_str = rel.get("to", "")
                    rel_type = rel.get("type", "relates_to")
                    output.append(f"- {from_str} → {to_str}: {rel_type}\n")

            # All memories section (for reference)
            output.append(f"\n## All Memories\n")
            for i, bubble in enumerate(bubbles[:10], 1):
                sector = bubble.get("sector", "")
                content = bubble.get("content", "")
                salience = bubble.get("salience", 0.5)
                output.append(f"\n{i}. [{sector}] {content[:100]}{'...' if len(content) > 100 else ''} (salience: {salience:.2f})\n")

            if len(bubbles) > 10:
                output.append(f"\n... and {len(bubbles) - 10} more memories\n")

            return "".join(output)

        except Exception as e:
            logger.error(f"Failed to retrieve memory relations: {e}", exc_info=True)
            return f"Error retrieving memory relations: {str(e)}"
