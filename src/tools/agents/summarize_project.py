"""
Summarize Project Tool.
MCP tool wrapper for the SummarizeAgent.
"""

import logging

from pydantic import Field

from src.agents.summarize_agent import SummarizeAgent
from src.database.queries.memory import search_bubbles

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

        This agent retrieves memories containing the project name,
        then uses AI to generate a structured summary including:
        - Overview
        - Key Decisions
        - Action Items
        - Notes

        The agent's behavior (model, prompt, format) can be configured
        in src/agents/summarize_agent.py without changing this code.
        """
        try:
            # Step 1: Retrieve memories related to the project
            memories = await search_bubbles(project, limit)

            if not memories:
                return f"No memories found for project '{project}'.\n\nTry using a different project name or add some memories first with create_memory."

            # Step 2: Format memories for the agent
            memories_text = "\n\n".join(
                [
                    f"- [{m.sector}] {m.content}\n  (Created: {m.created_at.strftime('%Y-%m-%d')}, Salience: {m.salience:.2f})"
                    for m in memories
                ]
            )

            # Step 3: Run the agent
            summary = await SummarizeAgent.run(project=project, memories=memories_text)

            # Step 4: Format and return the result
            output = [
                f"# Project Summary: {project}\n",
                f"**Source:** {len(memories)} memories analyzed\n",
                f"**Agent:** {SummarizeAgent.config.name}\n",
                f"**Model:** {SummarizeAgent.config.model}\n\n",
                "---\n\n",
                summary,
            ]

            return "".join(output)

        except Exception as e:
            logger.error(f"Failed to summarize project: {e}")
            return f"Error summarizing project: {str(e)}"
