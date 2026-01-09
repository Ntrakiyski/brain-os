"""
Summarize Project Tool.
MCP tool wrapper for the summarize_project PocketFlow.
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
            description="The project name to search for and summarize (e.g., 'Brain OS', 'website redesign')"
        ),
        limit: int = Field(default=20, description="Maximum number of memories to include", ge=1, le=100),
    ) -> str:
        """
        Summarize all memories related to a specific project.

        This tool retrieves memories containing the project name,
        then uses AI to generate a structured summary including:
        - Overview
        - Key Decisions
        - Action Items
        - Notes

        Powered by PocketFlow with AsyncNode/AsyncFlow patterns.
        Configuration can be modified in src/flows/summarize_project.py.
        """
        try:
            # Step 1: Retrieve memories related to the project
            memories = await search_bubbles(project, limit)

            if not memories:
                return f"No memories found for project '{project}'.\n\nTry using a different project name or add some memories first with create_memory."

            # Step 2: Format memories for the flow
            memories_text = "\n\n".join(
                [
                    f"- [{m.sector}] {m.content}\n  (Created: {m.created_at.strftime('%Y-%m-%d')}, Salience: {m.salience:.2f})"
                    for m in memories
                ]
            )

            # Step 3: Run the PocketFlow
            shared = {
                "neo4j_driver": get_driver(),
                "project_name": project,
                "memories": memories_text
            }

            await summarize_project_flow.run_async(shared)

            summary = shared.get("summary", "No summary generated")

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
