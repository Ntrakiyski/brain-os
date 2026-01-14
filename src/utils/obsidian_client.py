"""
Obsidian MCP client utility.
Connects to YuNaga224/obsidian-memory-mcp server via HTTP wrapper.

Phase 5.1: Basic Neo4j → Obsidian sync
Phase 6: Add cleanup/archive functionality for Obsidian entities
"""

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def sync_to_obsidian(
    entity_name: str,
    entity_type: str,
    content: str,
    observations: list[str],
    metadata: dict[str, Any],
) -> bool:
    """
    Sync a memory to Obsidian vault via HTTP.

    Args:
        entity_name: Clean filename for the entity
        entity_type: Cognitive sector (Episodic, Semantic, etc.)
        content: Main memory content
        observations: Supporting observations
        metadata: Additional YAML frontmatter (salience, neo4j_id, etc.)

    Returns:
        True if sync succeeded, False if failed (graceful degradation)
    """
    url = os.getenv("OBSIDIAN_MCP_URL", "http://obsidian-mcp:8001/mcp")

    try:
        async with asyncio.timeout(5):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "method": "tools/call",
                        "params": {
                            "name": "create_entities",
                            "arguments": {
                                "entities": [
                                    {
                                        "name": entity_name,
                                        "entityType": entity_type,
                                        "observations": observations,
                                        "metadata": {
                                            **metadata,
                                            "content": content,  # Put content in metadata
                                        },
                                    }
                                ]
                            },
                        },
                    },
                    timeout=5.0,
                )

                if response.status_code == 200:
                    logger.info(f"Synced to Obsidian: {entity_name}")
                    return True
                else:
                    logger.warning(
                        f"Obsidian sync failed: HTTP {response.status_code}: {response.text[:200]}"
                    )
                    return False

    except asyncio.TimeoutError:
        logger.warning("Obsidian sync timed out (5s)")
        return False
    except Exception as e:
        logger.warning(f"Obsidian sync error: {e}")
        return False  # Graceful degradation - Neo4j still worked


async def cleanup_obsidian_entities(
    entity_names: list[str],
    archive: bool = False
) -> dict[str, Any]:
    """
    Cleanup Obsidian entities by deleting or archiving them.

    Args:
        entity_names: List of entity names to cleanup
        archive: If True, move to Archived folder instead of deleting

    Returns:
        Dictionary with success status and details
    """
    url = os.getenv("OBSIDIAN_MCP_URL", "http://obsidian-mcp:8001/mcp")

    if not entity_names:
        return {"success": True, "message": "No entities to cleanup"}

    try:
        async with asyncio.timeout(10):
            async with httpx.AsyncClient() as client:
                if archive:
                    # Move to Archived folder by calling archive tool if available
                    # For now, we'll use delete since the obsidian-mcp doesn't have an archive function
                    # TODO: Implement archive functionality in obsidian-mcp
                    logger.info(f"Archive requested for {len(entity_names)} entities (deleting for now)")
                    response = await client.post(
                        url,
                        json={
                            "method": "tools/call",
                            "params": {
                                "name": "delete_entities",
                                "arguments": {
                                    "entityNames": entity_names
                                },
                            },
                        },
                        timeout=10.0,
                    )
                else:
                    # Delete entities
                    response = await client.post(
                        url,
                        json={
                            "method": "tools/call",
                            "params": {
                                "name": "delete_entities",
                                "arguments": {
                                    "entityNames": entity_names
                                },
                            },
                        },
                        timeout=10.0,
                    )

                if response.status_code == 200:
                    logger.info(f"Cleaned up {len(entity_names)} Obsidian entities (archive={archive})")
                    return {
                        "success": True,
                        "deleted_count": len(entity_names),
                        "archive": archive
                    }
                else:
                    logger.warning(
                        f"Obsidian cleanup failed: HTTP {response.status_code}: {response.text[:200]}"
                    )
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "details": response.text[:200]
                    }

    except asyncio.TimeoutError:
        logger.warning("Obsidian cleanup timed out (10s)")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        logger.warning(f"Obsidian cleanup error: {e}")
        return {"success": False, "error": str(e)}
