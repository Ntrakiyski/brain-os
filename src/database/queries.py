"""
Granular Cypher query functions for Brain OS.
Single-purpose database operations for bubbles and clouds.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from src.database.connection import get_connection
from src.utils.schemas import BubbleCreate, BubbleResponse

logger = logging.getLogger(__name__)


async def upsert_bubble(data: BubbleCreate) -> BubbleResponse:
    """
    Store a new memory bubble in Neo4j.

    Uses MERGE on content to avoid duplicates, or CREATE if new.
    Sets automatic timestamp fields for temporal evolution tracking.
    """
    conn = await get_connection()
    now = datetime.now(timezone.utc)

    cypher = """
    MERGE (b:Bubble {content: $content})
    ON CREATE SET
        b.sector = $sector,
        b.source = $source,
        b.salience = $salience,
        b.created_at = $now,
        b.valid_from = $now,
        b.valid_to = NULL
    ON MATCH SET
        b.salience = $salience,
        b.accessed_at = $now
    RETURN b
    """

    async with conn.session() as session:
        result = await session.run(
            cypher,
            content=data.content,
            sector=data.sector,
            source=data.source,
            salience=data.salience,
            now=now.isoformat()
        )
        record = await result.single()
        if record:
            node = record["b"]
            logger.info(f"Stored bubble: {data.content[:50]}...")
            return BubbleResponse(
                id=node.element_id,
                content=node["content"],
                sector=node["sector"],
                source=node["source"],
                salience=node["salience"],
                created_at=datetime.fromisoformat(node["created_at"]),
                valid_from=datetime.fromisoformat(node["valid_from"]),
                valid_to=None
            )
    raise RuntimeError("Failed to create bubble")


async def search_bubbles(query: str, limit: int = 10) -> list[BubbleResponse]:
    """
    Search for bubbles containing the query string.

    Uses CONTAINS for case-insensitive partial matching.
    Returns results ordered by recency (most recent first).
    """
    conn = await get_connection()

    cypher = """
    MATCH (b:Bubble)
    WHERE toLower(b.content) CONTAINS toLower($search_query)
    AND b.valid_to IS NULL
    RETURN b
    ORDER BY b.created_at DESC
    LIMIT $result_limit
    """

    async with conn.session() as session:
        result = await session.run(
            cypher,
            search_query=query,
            result_limit=limit
        )
        bubbles = []
        async for record in result:
            node = record["b"]
            bubbles.append(BubbleResponse(
                id=node.element_id,
                content=node["content"],
                sector=node["sector"],
                source=node["source"],
                salience=node["salience"],
                created_at=datetime.fromisoformat(node["created_at"]),
                valid_from=datetime.fromisoformat(node["valid_from"]),
                valid_to=datetime.fromisoformat(node["valid_to"]) if node.get("valid_to") else None
            ))
        logger.info(f"Found {len(bubbles)} bubbles for query: {query}")
        return bubbles


async def get_bubble_by_id(bubble_id: str) -> Optional[BubbleResponse]:
    """Retrieve a single bubble by its internal node ID."""
    conn = await get_connection()

    cypher = """
    MATCH (b:Bubble)
    WHERE element_id(b) = $bubble_id
    AND b.valid_to IS NULL
    RETURN b
    """

    async with conn.session() as session:
        result = await session.run(cypher, bubble_id=bubble_id)
        record = await result.single()
        if record:
            node = record["b"]
            return BubbleResponse(
                id=node.element_id,
                content=node["content"],
                sector=node["sector"],
                source=node["source"],
                salience=node["salience"],
                created_at=datetime.fromisoformat(node["created_at"]),
                valid_from=datetime.fromisoformat(node["valid_from"]),
                valid_to=datetime.fromisoformat(node["valid_to"]) if node.get("valid_to") else None
            )
    return None


async def get_all_bubbles(limit: int = 100) -> list[BubbleResponse]:
    """
    Retrieve all active bubbles from the database.

    Returns all bubbles ordered by recency (most recent first).
    Use limit to prevent unbounded result sets.
    """
    conn = await get_connection()

    cypher = """
    MATCH (b:Bubble)
    WHERE b.valid_to IS NULL
    RETURN b
    ORDER BY b.created_at DESC
    LIMIT $result_limit
    """

    async with conn.session() as session:
        result = await session.run(cypher, result_limit=limit)
        bubbles = []
        async for record in result:
            node = record["b"]
            bubbles.append(BubbleResponse(
                id=node.element_id,
                content=node["content"],
                sector=node["sector"],
                source=node["source"],
                salience=node["salience"],
                created_at=datetime.fromisoformat(node["created_at"]),
                valid_from=datetime.fromisoformat(node["valid_from"]),
                valid_to=datetime.fromisoformat(node["valid_to"]) if node.get("valid_to") else None
            ))
        logger.info(f"Retrieved {len(bubbles)} total bubbles")
        return bubbles
