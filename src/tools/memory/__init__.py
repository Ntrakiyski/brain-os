"""
Memory tools module.
Contains all memory-related MCP tools organized by function.
"""

from src.tools.memory.create_memory import register_create_memory
from src.tools.memory.get_memory import register_get_memory
from src.tools.memory.list_sectors import register_list_sectors
from src.tools.memory.visualize_memories import register_visualize_memory


def register_memory_tools(mcp) -> None:
    """
    Register all memory tools with the given FastMCP instance.

    This is the main entry point for memory tool registration.
    Call this function to add all memory tools to your MCP server.

    Args:
        mcp: The FastMCP instance to register tools with.
    """
    register_create_memory(mcp)
    register_get_memory(mcp)
    register_list_sectors(mcp)
    register_visualize_memory(mcp)


__all__ = ["register_memory_tools"]
