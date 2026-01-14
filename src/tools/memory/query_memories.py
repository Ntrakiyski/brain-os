"""
Query Memories Tool.
Phase 6: AI-powered Q&A with reasoning and confidence scores.

MCP tool wrapper for the query_memories flow.
Provides natural language Q&A interface to your memories.
"""

import logging
from typing import Optional

from pydantic import Field

from src.database.connection import get_driver
from src.flows.query_memories import (
    query_analysis_node,
    hybrid_retrieval_node,
    reflection_node,
    answer_synthesis_node
)

logger = logging.getLogger(__name__)


def register_query_memories(mcp) -> None:
    """Register the query_memories tool with FastMCP."""

    @mcp.tool
    async def query_memories_tool(
        query: str = Field(
            description="Your natural language question (e.g., 'When did I meet with Alice?', 'Why did I choose PostgreSQL?', 'Summarize my work with FastTrack')"
        ),
        conversation_history: Optional[list[str]] = Field(
            default=[],
            description="Recent messages for context (helps with pronouns like 'it', 'they', 'we'). Up to last 5 messages."
        ),
    ) -> str:
        """
        AI-powered Q&A with reasoning and confidence scores.

        **Use this for direct questions requiring answers.**

        This tool analyzes your question, retrieves relevant memories, and
        generates a direct answer with full reasoning trace and confidence score.

        When to Use This:
        ✓ Direct questions ("When did I...?", "Why did we...?")
        ✓ Decision rationale ("Why did I choose X?")
        ✓ Summaries ("Summarize my work with...")
        ✓ Opinion queries ("What do I think about...?")
        ✓ Temporal queries ("What happened last week?")

        When NOT to Use This:
        ✗ Quick keyword lookup (use get_memory - faster)
        ✗ Deep context exploration (use get_memory_relations)
        ✗ Starting work on project (use get_instinctive_memory)

        Response Format:
        - Answer: Direct response to your question
        - Reasoning: Step-by-step reasoning with memory references [1], [2]
        - Confidence: Score from 0.0-1.0 with label (Very Confident → Uncertain)
        - Sources: Number of memories used

        Speed: ~2-6 seconds (uses LLM for synthesis)
        """
        try:
            # Phase 4: Enhanced logging
            logger.debug(f"query_memories_tool: Query='{query}', history_len={len(conversation_history)}")

            # Prepare shared store for the flow
            shared = {
                "query": query,
                "conversation_history": conversation_history or [],
                "neo4j_driver": get_driver()
            }

            # Step 1: Query Analysis
            logger.info("Step 1: Analyzing query...")
            analysis_result = await query_analysis_node.exec_async((query, conversation_history))
            shared["query_analysis"] = analysis_result
            shared["original_query"] = query

            # Step 2: Hybrid Retrieval
            logger.info("Step 2: Retrieving memories...")
            concepts = analysis_result.get("key_concepts", [])
            entities = analysis_result.get("extracted_entities", [])
            search_terms = " ".join([query] + concepts + entities)

            retrieved = await hybrid_retrieval_node.exec_async(search_terms)
            shared["retrieved_memories"] = retrieved
            shared["initial_result_count"] = len(retrieved)

            # Step 3: Reflection (if needed)
            complexity = analysis_result.get("complexity", "simple")
            if complexity == "complex" and len(retrieved) < 3:
                logger.info("Step 3: Reflection triggered for complex query...")
                reflection_result = await reflection_node.exec_async((query, retrieved, True))

                if reflection_result:
                    # Retrieve additional memories
                    from src.database.queries.memory import search_bubbles
                    all_additional = []
                    for concept in reflection_result[:3]:
                        results = await search_bubbles(query=concept, limit=5)
                        all_additional.extend(results)

                    # Remove duplicates
                    existing_ids = {m.id for m in retrieved}
                    additional = [m for m in all_additional if m.id not in existing_ids]
                    shared["reflection_memories"] = additional
                    retrieved.extend(additional)
                    logger.info(f"Reflection added {len(additional)} memories")
            else:
                logger.info("Step 3: Skipped (sufficient results)")
                shared["reflection_memories"] = []

            # Step 4: Answer Synthesis
            logger.info("Step 4: Synthesizing answer...")
            result = await answer_synthesis_node.exec_async((
                query,
                analysis_result,
                retrieved
            ))

            # Format the output
            output = format_query_result(result, query)

            logger.info(f"query_memories_tool: Answer generated (confidence={result.get('confidence', 0):.2f})")

            return output

        except Exception as e:
            logger.error(f"query_memories_tool failed: {e}", exc_info=True)
            return f"""## Error

I encountered an error processing your question: "{query}"

Error details: {str(e)}

Please try:
1. Rephrasing your question
2. Using get_memory for keyword search
3. Using get_memory_relations for deep exploration"""


def format_query_result(result: dict, query: str) -> str:
    """Format the query result for display."""
    answer = result.get("answer", "")
    reasoning = result.get("reasoning", "")
    confidence = result.get("confidence", 0.0)
    label = result.get("confidence_label", "Unknown")
    num_used = result.get("num_memories_used", 0)

    if confidence == 0.0 and not answer:
        # No results case
        return f"""## No Results Found

{reasoning}

Try:
- Rephrasing your question with different keywords
- Using get_memory for keyword search
- Using get_all_memories to see what's stored
- Using get_memory_relations for broader exploration
"""

    output_parts = [
        f"## Answer\n{answer}\n",
        f"## Reasoning\n{reasoning}\n",
        f"## Confidence\n{confidence:.2f} / 1.0 ({label})\n",
        f"## Sources\n{num_used} memory entries used"
    ]

    return "\n".join(output_parts)
