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
            description="What you're looking for (e.g., 'Project A technology decisions')"
        ),
        conversation_history: List[str] = Field(
            default=[],
            description="Recent messages for context (last 5-10 recommended)"
        ),
        time_scope: str = Field(
            default="auto",
            description="Time filter: 'recent' (30 days), 'all_time', or 'auto' (let AI decide)"
        ),
        salience_filter: str = Field(
            default="auto",
            description="Salience filter: 'high' (>0.6), 'any', or 'auto' (let AI decide)"
        ),
    ) -> str:
        """
        Deep memory retrieval with contextual understanding.

        This is different from get_memory:
        - **Pre-query**: Analyzes context and expands/narrows search intelligently
        - **Query**: Neo4j with smart filters based on conversation context
        - **Post-query**: Synthesizes results and finds relationships

        Use this when you need comprehensive, context-aware retrieval.
        Use get_memory for simple, direct searches.

        **Example contexts where this shines**:
        - "Why did I choose X over Y?" (finds decision + rationale)
        - "How do I deploy this?" (finds all deployment-related memories)
        - "What are the key decisions?" (finds high-salience memories)

        **How it works**:
        1. Pre-query agent analyzes your query and conversation history (~100ms)
        2. Query agent searches Neo4j with expanded context
        3. Post-query agent synthesizes results and identifies relationships (~2-5s)
        """
        try:
            # Run the contextual retrieval flow
            shared = {
                "neo4j_driver": get_driver(),
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
