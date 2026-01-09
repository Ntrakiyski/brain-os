"""
Granular Cypher query functions for Brain OS.
Single-purpose database operations for bubbles and clouds.

Phase 3 Enhanced: Supports memory_type, activation_threshold, entities, observations.
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

    Phase 3 Enhanced: Stores memory_type, activation_threshold, entities, observations.
    Uses MERGE on content to avoid duplicates, or CREATE if new.
    Sets automatic timestamp fields for temporal evolution tracking.
    """
    conn = await get_connection()
    now = datetime.now(timezone.utc)

    # Auto-calculate activation_threshold if not provided
    activation_threshold = data.activation_threshold
    if activation_threshold is None:
        thresholds = {
            "instinctive": 0.25,
            "thinking": 0.65,
            "dormant": 0.90,
        }
        activation_threshold = thresholds.get(data.memory_type, 0.65)

    cypher = """
    MERGE (b:Bubble {content: $content})
    ON CREATE SET
        b.sector = $sector,
        b.source = $source,
        b.salience = $salience,
        b.memory_type = $memory_type,
        b.activation_threshold = $activation_threshold,
        b.entities = $entities,
        b.observations = $observations,
        b.created_at = $now,
        b.valid_from = $now,
        b.valid_to = NULL,
        b.access_count = 0,
        b.last_accessed = NULL
    ON MATCH SET
        b.salience = $salience,
        b.accessed_at = $now,
        b.access_count = coalesce(b.access_count, 0) + 1,
        b.last_accessed = $now
    RETURN b
    """

    async with conn.session() as session:
        result = await session.run(
            cypher,
            content=data.content,
            sector=data.sector,
            source=data.source,
            salience=data.salience,
            memory_type=data.memory_type,
            activation_threshold=activation_threshold,
            entities=data.entities or [],
            observations=data.observations or [],
            now=now.isoformat()
        )
        record = await result.single()
        if record:
            node = record["b"]
            logger.info(f"Stored bubble (type={data.memory_type}): {data.content[:50]}...")
            return BubbleResponse(
                id=node.element_id,
                content=node["content"],
                sector=node["sector"],
                source=node["source"],
                salience=node["salience"],
                created_at=datetime.fromisoformat(node["created_at"]),
                valid_from=datetime.fromisoformat(node["valid_from"]),
                valid_to=None,
                memory_type=node.get("memory_type", "thinking"),
                activation_threshold=node.get("activation_threshold", 0.65),
                entities=node.get("entities", []),
                observations=node.get("observations", []),
                accessed_count=node.get("access_count", 0),
                last_accessed=node.get("last_accessed")
            )
    raise RuntimeError("Failed to create bubble")


async def search_bubbles(query: str, limit: int = 10, memory_type: Optional[str] = None) -> list[BubbleResponse]:
    """
    Search for bubbles containing the query string.

    Phase 3 Enhanced: Optional filtering by memory_type.
    Uses CONTAINS for case-insensitive partial matching.
    Returns results ordered by recency (most recent first).

    Args:
        query: Search term
        limit: Maximum results
        memory_type: Optional filter for memory type (instinctive/thinking/dormant)
    """
    conn = await get_connection()

    # Build dynamic query based on filters
    where_clauses = [
        "toLower(b.content) CONTAINS toLower($search_query)",
        "b.valid_to IS NULL"
    ]

    if memory_type:
        where_clauses.append("b.memory_type = $memory_type")

    where_clause = " AND ".join(where_clauses)

    cypher = f"""
    MATCH (b:Bubble)
    WHERE {where_clause}
    RETURN b
    ORDER BY b.created_at DESC
    LIMIT $result_limit
    """

    params = {
        "search_query": query,
        "result_limit": limit
    }
    if memory_type:
        params["memory_type"] = memory_type

    async with conn.session() as session:
        result = await session.run(cypher, **params)
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
                valid_to=datetime.fromisoformat(node["valid_to"]) if node.get("valid_to") else None,
                memory_type=node.get("memory_type", "thinking"),
                activation_threshold=node.get("activation_threshold", 0.65),
                entities=node.get("entities", []),
                observations=node.get("observations", []),
                accessed_count=node.get("access_count", 0),
                last_accessed=node.get("last_accessed")
            ))
        logger.info(f"Found {len(bubbles)} bubbles for query: {query}")
        return bubbles


async def get_bubble_by_id(bubble_id: str) -> Optional[BubbleResponse]:
    """Retrieve a single bubble by its internal node ID.

    Phase 3 Enhanced: Returns all fields including memory_type and activation_threshold.
    """
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
                valid_to=datetime.fromisoformat(node["valid_to"]) if node.get("valid_to") else None,
                memory_type=node.get("memory_type", "thinking"),
                activation_threshold=node.get("activation_threshold", 0.65),
                entities=node.get("entities", []),
                observations=node.get("observations", []),
                accessed_count=node.get("access_count", 0),
                last_accessed=node.get("last_accessed")
            )
    return None


async def get_all_bubbles(limit: int = 100) -> list[BubbleResponse]:
    """
    Retrieve all active bubbles from the database.

    Phase 3 Enhanced: Returns all fields including memory_type.
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
                valid_to=datetime.fromisoformat(node["valid_to"]) if node.get("valid_to") else None,
                memory_type=node.get("memory_type", "thinking"),
                activation_threshold=node.get("activation_threshold", 0.65),
                entities=node.get("entities", []),
                observations=node.get("observations", []),
                accessed_count=node.get("access_count", 0),
                last_accessed=node.get("last_accessed")
            ))
        logger.info(f"Retrieved {len(bubbles)} total bubbles")
        return bubbles


async def search_instinctive_bubbles(concepts: list[str], salience_threshold: float = 0.5, limit: int = 10) -> list[BubbleResponse]:
    """
    Search for instinctive bubbles that match given concepts.

    Phase 3 Enhanced: Searches in content, entities, observations, and sector.

    Args:
        concepts: List of concept strings to match
        salience_threshold: Minimum salience score (0.0-1.0)
        limit: Maximum results

    Returns:
        List of instinctive bubbles matching the concepts
    """
    conn = await get_connection()

    # Build dynamic WHERE clause with OR conditions for each concept
    # Search in: content, entities (array), observations (array), sector
    concept_conditions = " OR ".join([
        f"toLower(b.content) CONTAINS toLower($concept{i})"
        f" OR toLower(b.sector) CONTAINS toLower($concept{i})"
        f" OR ANY(entity IN b.entities WHERE toLower(entity) CONTAINS toLower($concept{i}))"
        f" OR ANY(obs IN b.observations WHERE toLower(obs) CONTAINS toLower($concept{i}))"
        for i in range(len(concepts))
    ])

    cypher = f"""
    MATCH (b:Bubble)
    WHERE b.memory_type = 'instinctive'
    AND b.activation_threshold < $salience_threshold
    AND b.valid_to IS NULL
    AND ({concept_conditions})
    RETURN b
    ORDER BY b.salience DESC
    LIMIT $result_limit
    """

    params = {"salience_threshold": salience_threshold, "result_limit": limit}
    for i, concept in enumerate(concepts):
        params[f"concept{i}"] = concept

    async with conn.session() as session:
        result = await session.run(cypher, **params)
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
                valid_to=None,
                memory_type=node.get("memory_type", "instinctive"),
                activation_threshold=node.get("activation_threshold", 0.25),
                entities=node.get("entities", []),
                observations=node.get("observations", []),
                accessed_count=node.get("access_count", 0),
                last_accessed=node.get("last_accessed")
            ))
        logger.info(f"Found {len(bubbles)} instinctive bubbles for concepts: {concepts}")
        return bubbles


async def delete_bubble(bubble_id: str) -> bool:
    """
    Delete a single bubble by its internal node ID.

    Uses soft deletion by setting valid_to timestamp.
    This preserves audit trail and maintains temporal evolution tracking.

    Args:
        bubble_id: The numeric node ID (element_id) of the bubble

    Returns:
        True if deleted, False if not found
    """
    conn = await get_connection()
    now = datetime.now(timezone.utc)

    cypher = """
    MATCH (b:Bubble)
    WHERE element_id(b) = $bubble_id
    AND b.valid_to IS NULL
    SET b.valid_to = $now
    RETURN b.content as content
    """

    async with conn.session() as session:
        result = await session.run(cypher, bubble_id=bubble_id, now=now.isoformat())
        record = await result.single()
        if record:
            logger.info(f"Deleted bubble {bubble_id}: {record['content'][:50]}...")
            return True
        logger.warning(f"Bubble {bubble_id} not found for deletion")
        return False


async def delete_all_bubbles() -> int:
    """
    Delete all active bubbles from the database.

    Uses soft deletion by setting valid_to timestamp on all bubbles.
    This preserves audit trail and maintains temporal evolution tracking.

    Returns:
        Number of bubbles deleted
    """
    conn = await get_connection()
    now = datetime.now(timezone.utc)

    cypher = """
    MATCH (b:Bubble)
    WHERE b.valid_to IS NULL
    SET b.valid_to = $now
    RETURN count(b) as deleted_count
    """

    async with conn.session() as session:
        result = await session.run(cypher, now=now.isoformat())
        record = await result.single()
        count = record["deleted_count"] if record else 0
        logger.info(f"Deleted all {count} bubbles")
        return count


async def get_bubble_count(sector: Optional[str] = None) -> int:
    """
    Count active bubbles in the database, optionally filtered by sector.

    Used for visualization resources and statistics.

    Args:
        sector: Optional sector name to filter by (Episodic, Semantic, etc.)

    Returns:
        Count of active bubbles
    """
    conn = await get_connection()

    if sector:
        cypher = """
        MATCH (b:Bubble)
        WHERE b.sector = $sector
        AND b.valid_to IS NULL
        RETURN count(b) as bubble_count
        """
        params = {"sector": sector}
    else:
        cypher = """
        MATCH (b:Bubble)
        WHERE b.valid_to IS NULL
        RETURN count(b) as bubble_count
        """
        params = {}

    async with conn.session() as session:
        result = await session.run(cypher, **params)
        record = await result.single()
        count = record["bubble_count"] if record else 0
        logger.debug(f"Counted {count} bubbles" + (f" in sector {sector}" if sector else ""))
        return count
