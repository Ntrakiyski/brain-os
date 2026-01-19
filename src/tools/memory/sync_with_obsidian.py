"""
Sync with Obsidian wrapper tool.
Triggers bidirectional sync with Obsidian MCP server.

Phase 2 Sync: Wrapper that calls the Obsidian MCP's sync_obsidian_neo4j tool.
"""

import json
import logging
import os
from pydantic import Field

from src.utils.observability import instrument_mcp_tool

logger = logging.getLogger(__name__)


def register_sync_with_obsidian(mcp) -> None:
    """Register the sync_with_obsidian tool with FastMCP."""

    @mcp.tool
    @instrument_mcp_tool("sync_with_obsidian")
    async def sync_with_obsidian(
        direction: str = Field(
            default="both",
            description="Sync direction: 'neo4j_to_obsidian' (Neo4j → Obsidian), 'obsidian_to_neo4j' (Obsidian → Neo4j), or 'both' (bidirectional)"
        ),
    ) -> str:
        """
        Trigger bidirectional sync with Obsidian MCP server.

        **Use this to manually trigger sync between Neo4j and Obsidian markdown files.**

        Sync Directions:

        **neo4j_to_obsidian**:
        - Fetches memories from Neo4j
        - Creates/updates corresponding markdown files in Obsidian vault
        - Use after creating new memories in Neo4j

        **obsidian_to_neo4j**:
        - Reads changed markdown files from Obsidian vault
        - Updates observations in Neo4j memories
        - Use after editing observations in Obsidian

        **both** (default):
        - Performs bidirectional sync
        - First: Neo4j → Obsidian
        - Then: Obsidian → Neo4j
        - Use for full synchronization

        Configuration:
        - Set OBSIDIAN_MCP_URL environment variable to the Obsidian MCP server endpoint
        - Default: https://obsidian-mcp.trakiyski.work/mcp
        """
        try:
            import httpx

            obsidian_url = os.getenv("OBSIDIAN_MCP_URL", "https://obsidian-mcp.trakiyski.work/mcp")

            logger.info(f"Sync with Obsidian: direction={direction}, url={obsidian_url}")

            async with httpx.AsyncClient(timeout=60.0) as client:
                # Call the Obsidian MCP sync tool via HTTP
                response = await client.post(
                    obsidian_url,
                    json={
                        "method": "tools/call",
                        "params": {
                            "name": "sync_obsidian_neo4j",
                            "arguments": {"direction": direction}
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    # Parse the MCP response format
                    if "result" in result and "content" in result["result"]:
                        content = result["result"]["content"][0]["text"]
                        try:
                            sync_data = json.loads(content)  # Safe JSON parsing
                            return (
                                f"Sync completed successfully!\n"
                                f"- Direction: {direction}\n"
                                f"- Duration: {sync_data.get('duration_ms', 0)}ms\n"
                                f"- Neo4j → Obsidian: {sync_data.get('neo4j_to_obsidian', {}).get('fetched', 0)} fetched, "
                                f"{sync_data.get('neo4j_to_obsidian', {}).get('created', 0)} created, "
                                f"{sync_data.get('neo4j_to_obsidian', {}).get('updated', 0)} updated\n"
                                f"- Obsidian → Neo4j: {sync_data.get('obsidian_to_neo4j', {}).get('changed_files', 0)} files, "
                                f"{sync_data.get('obsidian_to_neo4j', {}).get('updated_memories', 0)} memories updated"
                            )
                        except (json.JSONDecodeError, KeyError, TypeError) as e:
                            logger.warning(f"Failed to parse sync result: {e}")
                            return f"Sync completed (raw): {content}"
                    else:
                        return f"Sync completed (raw): {result}"
                else:
                    error_text = response.text
                    logger.error(f"Sync failed: HTTP {response.status_code} - {error_text}")
                    return f"Sync failed: HTTP {response.status_code} - {error_text}"

        except ImportError as e:
            logger.error(f"Import error: {e}")
            return f"Error: Required package not available. {str(e)}"
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return f"Sync error: {str(e)}"
