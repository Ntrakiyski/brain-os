"""
Memory deletion tools.
Delete individual memories or all memories from the Synaptic Graph.
"""

import logging

from pydantic import Field

from src.database.queries.memory import delete_bubble, delete_all_bubbles, get_bubble_by_id

logger = logging.getLogger(__name__)


def register_delete_memory(mcp) -> None:
    """Register the delete_memory and delete_all_memories tools with FastMCP."""

    @mcp.tool
    async def delete_memory(
        bubble_id: str = Field(
            description="Simple numeric Bubble ID (e.g., '4'). Get this from get_memory or get_all_memories results."
        ),
        confirm: bool = Field(
            default=False,
            description="Set to True to confirm deletion. This prevents accidental deletion."
        ),
    ) -> str:
        """
        Delete a specific memory from the Synaptic Graph.

        **DANGER**: This is a destructive operation. Use with caution.

        Finding Bubble IDs:
        - Run get_all_memories() - IDs are simple numbers like "4"
        - Run get_memory(query="your search") - IDs shown in results
        - Just use the numeric ID shown in the output

        Soft Deletion:
        This uses soft deletion (sets valid_to timestamp) which:
        - Preserves audit trail
        - Maintains temporal evolution tracking
        - Allows for potential recovery

        When to Use This:
        ✓ Memory is no longer relevant
        ✓ Memory contains incorrect information
        ✓ Memory was created in error
        ✓ Testing/development cleanup

        When NOT to Use This:
        ✗ Just want to hide temporarily (memories aren't shown unless retrieved)
        ✗ Memory might be needed later (consider updating instead)
        ✗ Bulk cleanup (use delete_all_memories with confirmation)

        Example Usage:
        1. get_all_memories(limit=10) → Find ID: "4"
        2. delete_memory(bubble_id="4", confirm=True) → Delete memory 4

        Returns:
        - Success: Confirmation with deleted memory content
        - Not found: Error message
        - No confirmation: Warning to set confirm=True
        """
        if not confirm:
            return """⚠️ **Deletion Not Confirmed**

To prevent accidental deletion, you must set confirm=True:

```python
delete_memory(bubble_id="4", confirm=True)
```

This extra step ensures you really want to delete this memory.

**To find bubble IDs**:
- Use get_all_memories() to see all memories
- Use get_memory(query="...") to search
- Look for the simple numeric ID shown in results
"""

        try:
            # Extract numeric ID from various bubble_id formats
            bubble_id_numeric = str(bubble_id).split(":")[0]
            try:
                bubble_id_numeric = int(bubble_id_numeric)
            except ValueError:
                return f"""## Error

Invalid bubble ID format: '{bubble_id}'

**Expected format:**
- Simple numeric ID like "4" or "123"

**To find bubble IDs**:
- Use get_memory to search for memories
- Use get_all_memories to see all memories
- Look for the simple numeric ID shown in the results
"""

            # First, retrieve the bubble to show what will be deleted
            bubble = await get_bubble_by_id(bubble_id_numeric)

            if not bubble:
                return f"""## Error

No memory found with ID: {bubble_id_numeric}

**To find valid bubble IDs**:
- Use get_memory to search for memories
- Use get_all_memories to see all memories
- Look for the numeric ID at the start of the element_id
"""

            # Store content for confirmation message
            content_preview = bubble.content[:100]
            sector = bubble.sector

            # Perform the deletion
            deleted = await delete_bubble(bubble_id_numeric)

            if deleted:
                return f"""## Memory Deleted Successfully

**ID**: {bubble_id_numeric}
**Sector**: {sector}
**Content**: {content_preview}{'...' if len(bubble.content) > 100 else ''}

The memory has been soft-deleted (valid_to timestamp set).
Audit trail is preserved in the database.
"""
            else:
                return f"## Error: Failed to delete memory with ID {bubble_id_numeric}"

        except Exception as e:
            logger.error(f"Failed to delete memory: {e}", exc_info=True)
            return f"## Error deleting memory: {str(e)}"

    @mcp.tool
    async def delete_all_memories(
        cleanup_obsidian: bool = Field(
            default=False,
            description="If True, also delete corresponding Obsidian .md files"
        ),
    ) -> str:
        """
        Delete ALL memories from the Synaptic Graph.

        **DANGER**: This is a destructive operation that affects ALL memories.

        Soft Deletion:
        This uses soft deletion (sets valid_to timestamp) which:
        - Preserves audit trail
        - Maintains temporal evolution tracking
        - Allows for potential recovery (with database access)

        Obsidian Integration:
        - cleanup_obsidian: If True, also deletes corresponding .md files from Obsidian vault

        Returns:
        - Success: Number of memories deleted
        - Error: Failure details
        """
        try:
            # First, get count of memories to be deleted
            from src.database.queries.memory import get_all_bubbles
            existing_memories = await get_all_bubbles(limit=1000)
            count = len(existing_memories)

            if count == 0:
                return """## No Memories to Delete

There are no memories in the system.

Nothing to delete.
"""

            # Perform the deletion
            deleted_count = await delete_all_bubbles(
                cleanup_obsidian=cleanup_obsidian
            )

            obsidian_message = ""
            if cleanup_obsidian:
                obsidian_message = f"""
**Obsidian**: All corresponding .md files deleted
"""
            else:
                obsidian_message = """
**Obsidian**: .md files NOT deleted (set cleanup_obsidian=True to delete)
"""

            return f"""## All Memories Deleted Successfully

**Deleted**: {deleted_count} memories{obsidian_message}

The Synaptic Graph has been cleared.
All memories have been soft-deleted (valid_to timestamp set).

Audit trail is preserved in the database.
You can now start fresh with new memories.

**Next Steps**:
- Create new memories with create_memory()
- Run get_all_memories() to confirm deletion
"""

        except Exception as e:
            logger.error(f"Failed to delete all memories: {e}", exc_info=True)
            return f"## Error deleting all memories: {str(e)}"
