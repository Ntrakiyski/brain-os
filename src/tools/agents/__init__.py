"""
Agent tools module.
Contains MCP tools that wrap PocketFlow agents.
"""

from src.tools.agents.summarize_project import register_summarize_project

__all__ = ["register_summarize_project"]


def register_agent_tools(mcp) -> None:
    """
    Register all agent-based tools with the given FastMCP instance.

    Args:
        mcp: The FastMCP instance to register tools with.
    """
    register_summarize_project(mcp)
