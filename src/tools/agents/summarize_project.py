"""
Summarize Project Tool.
MCP tool wrapper for the summarize_project PocketFlow.

Phase 4 Enhancement: Added enhanced logging and progress tracking.
"""

import logging

from pydantic import Field

from src.database.connection import get_driver
from src.database.queries.memory import search_bubbles
from src.flows.summarize_project import summarize_project_flow

logger = logging.getLogger(__name__)


def register_summarize_project(mcp) -> None:
    """Register the summarize_project tool with FastMCP."""

    @mcp.tool
    async def summarize_project(
        project: str = Field(
            description="Project name to search for and summarize. Must match entity names used in memories (e.g., 'FastTrack', 'BrainOS', 'website redesign')"
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=100,
            description="Maximum memories to include (1-100). Use 10-20 for small projects, 30-50 for large projects"
        ),
    ) -> str:
        """
        AI-powered project summaries using retrieved memories.

        **Use this when returning to a project after a break.**

        This tool:
        1. Searches for memories containing the project name
        2. Formats memories for PocketFlow processing
        3. Runs PocketFlow with OpenRouter CREATIVE model
        4. Generates structured summary with sections

        Output Sections:
        - Overview: Project description and context
        - Key Decisions: Major choices with rationale
        - Action Items: Outstanding tasks and next steps
        - Notes: Client info, budget, timeline

        When to Use This:
        ✓ Starting work on a project after a break
        ✓ Onboarding to an existing project
        ✓ Preparing status reports
        ✓ Understanding project patterns

        When NOT to Use This:
        ✗ Quick memory lookup (use get_memory)
        ✗ Decision rationale (use get_memory_relations)
        ✗ Context switching (use get_instinctive_memory)

        Best Practices:
        1. Use consistent project names across memories
        2. Include project name in entities when creating memories
        3. Adjust limit based on project size
        4. Review generated summary for accuracy

        Speed: ~3-10 seconds (uses OpenRouter CREATIVE model)

        Example:
        - create_memory(entities=["FastTrack", "pricing"], ...)
        - create_memory(entities=["FastTrack", "N8N"], ...)
        - summarize_project(project="FastTrack", limit=10)
        """
        try:
            # Phase 4: Enhanced logging
            logger.debug(f"summarize_project: Starting for project '{project}'")
            logger.info(f"Starting project summary: {project}")

            # Step 1: Retrieve memories related to the project
            logger.debug(f"summarize_project: Retrieving memories (limit={limit})")
            memories = await search_bubbles(project, limit)

            if not memories:
                logger.warning(f"No memories found for project '{project}'")
                return f"No memories found for project '{project}'.\n\nTry using a different project name or add some memories first with create_memory."

            # Progress: 30% - Memories retrieved
            logger.info(f"Found {len(memories)} memories for {project}")

            # Step 2: Format memories for the flow
            logger.debug("summarize_project: Formatting memories for PocketFlow")
            memories_text = "\n\n".join(
                [
                    f"- [{m.sector}] {m.content}\n  (Created: {m.created_at.strftime('%Y-%m-%d')}, Salience: {m.salience:.2f})"
                    for m in memories
                ]
            )

            # Step 3: Run the PocketFlow
            logger.debug("summarize_project: Calling PocketFlow for LLM synthesis")
            shared = {
                "neo4j_driver": get_driver(),
                "project_name": project,
                "memories": memories_text
            }

            await summarize_project_flow.run_async(shared)

            summary = shared.get("summary", "No summary generated")

            # Progress: 100% - Complete
            logger.info("Summary formatting complete")
            logger.debug(f"summarize_project: Complete - {len(memories)} memories processed")

            # Step 4: Format and return the result
            output = [
                f"# Project Summary: {project}\n",
                f"**Source:** {len(memories)} memories analyzed\n",
                f"**Flow:** summarize_project_flow (PocketFlow)\n\n",
                "---\n\n",
                summary,
            ]

            return "".join(output)

        except Exception as e:
            logger.error(f"Failed to summarize project: {e}", exc_info=True)
            return f"Error summarizing project: {str(e)}"
