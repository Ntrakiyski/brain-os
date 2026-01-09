"""
Memory tools module.
Contains all memory-related MCP tools organized by function.

Phase 3 Enhanced: Includes instinctive memory activation and contextual retrieval.
"""

from src.tools.memory.create_memory import register_create_memory
from src.tools.memory.get_memory import register_get_memory
from src.tools.memory.list_sectors import register_list_sectors
from src.tools.memory.visualize_memories import register_visualize_memory

# Phase 3 tools
from src.tools.memory.instinctive_memory import register_instinctive_memory
from src.tools.memory.get_relations import register_get_memory_relations
from src.tools.memory.visualize_relations import register_visualize_relations

# Deletion tools
from src.tools.memory.delete_memory import register_delete_memory


def register_memory_tools(mcp) -> None:
    """
    Register all memory tools with the given FastMCP instance.

    This is the main entry point for memory tool registration.
    Call this function to add all memory tools to your MCP server.

    Args:
        mcp: The FastMCP instance to register tools with.
    """
    # Phase 2 tools
    register_create_memory(mcp)
    register_get_memory(mcp)
    register_list_sectors(mcp)
    register_visualize_memory(mcp)

    # Phase 3 tools
    register_instinctive_memory(mcp)
    register_get_memory_relations(mcp)
    register_visualize_relations(mcp)

    # Deletion tools
    register_delete_memory(mcp)


__all__ = ["register_memory_tools"]
