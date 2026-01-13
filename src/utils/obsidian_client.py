"""
Obsidian MCP client utility.
Connects to YuNaga224/obsidian-memory-mcp server via HTTP wrapper.

Phase 5.1: Basic Neo4j → Obsidian sync
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
