# Phase 1: Code Snippets & Key Patterns

This document captures the most important and complex code patterns implemented during Phase 1. These snippets serve as reference implementations for future development.

---

## Table of Contents
1. [Configuration Management](#1-configuration-management)
2. [Neo4j Connection Pool](#2-neo4j-connection-pool)
3. [Cypher Query Patterns](#3-cypher-query-patterns)
4. [Pydantic Validation](#4-pydantic-validation)
5. [FastMCP Tool Definition](#5-fastmcp-tool-definition)
6. [Claude Desktop Entry Point](#6-claude-desktop-entry-point)

---

## 1. Configuration Management

### Frozen Dataclass Pattern with Environment Loading

**File:** `src/core/config.py`

```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class Neo4jConfig:
    """Neo4j database configuration.

    Frozen dataclass ensures configuration is immutable after initialization,
    preventing accidental modifications at runtime.
    """
    uri: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        """Factory method that loads configuration from environment variables.

        Provides sensible defaults for local development while requiring
        explicit values in production.
        """
        return cls(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "brainos_password_123")
        )


@dataclass(frozen=True)
class GroqConfig:
    """Groq API configuration for fast actions (System 1)."""
    api_key: str
    quick_model: str

    @classmethod
    def from_env(cls) -> "GroqConfig":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return cls(
            api_key=api_key,
            quick_model=os.getenv("GROQ_QUICK_MODEL", "openai/gpt-oss-120b")
        )


# Global configuration instances - loaded once at module import
neo4j = Neo4jConfig.from_env()
groq = GroqConfig.from_env()


# Five-sector ontology constants
VALID_SECTORS = {
    "Episodic",
    "Semantic",
    "Procedural",
    "Emotional",
    "Reflective",
}
```

**Key Design Decisions:**
- **Frozen dataclasses**: Immutability prevents runtime configuration drift
- **Factory methods**: `from_env()` encapsulates environment loading logic
- **Global instances**: Configuration loaded once at import, not per-request
- **Explicit errors**: Missing API keys fail fast with clear error messages

---

## 2. Neo4j Connection Pool

### Async Connection Singleton with Lifecycle Management

**File:** `src/database/connection.py`

```python
import logging
from typing import Optional
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable

from src.core.config import neo4j

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Async Neo4j connection manager.

    Wraps the Neo4j driver and provides:
    - Async context management for connections
    - Session creation for query execution
    - Graceful shutdown handling
    """

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncGraphDatabase.driver] = None

    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connectivity immediately
            await self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    def session(self):
        """Get a new async session from the driver.

        Sessions are lightweight and should be created per-operation.
        The driver handles connection pooling internally.
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized. Call connect() first.")
        return self.driver.session()


# Global connection instance (module-level singleton)
_connection: Optional[Neo4jConnection] = None


async def get_connection() -> Neo4jConnection:
    """Get or create the global Neo4j connection.

    Implements lazy initialization pattern:
    - First call creates the connection
    - Subsequent calls reuse the existing connection
    - Driver maintains internal connection pool

    Returns:
        Neo4jConnection: The active connection manager
    """
    global _connection
    if _connection is None:
        _connection = Neo4jConnection(
            uri=neo4j.uri,
            user=neo4j.user,
            password=neo4j.password
        )
        await _connection.connect()
    return _connection


async def close_connection() -> None:
    """Close the global Neo4j connection.

    Call this during application shutdown (e.g., in FastMCP lifespan context).
    """
    global _connection
    if _connection:
        await _connection.close()
        _connection = None
```

**Key Design Decisions:**
- **Singleton pattern**: Single driver instance for the application lifetime
- **Lazy initialization**: Connection established on first use, not at import
- **Session-per-query**: Lightweight sessions created for each operation
- **Connection pooling**: Driver internally manages connection pool
- **Graceful shutdown**: Explicit close method for cleanup during shutdown

---

## 3. Cypher Query Patterns

### Upsert with MERGE (Create or Update)

**File:** `src/database/queries.py:16-64`

```python
async def upsert_bubble(data: BubbleCreate) -> BubbleResponse:
    """
    Store a new memory bubble in Neo4j.

    Uses MERGE on content to avoid duplicates, or CREATE if new.
    Sets automatic timestamp fields for temporal evolution tracking.

    Key behavior:
    - ON CREATE: Sets initial timestamps and sector
    - ON MATCH: Updates salience and accessed_at (reinforces memory)
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
            return BubbleResponse(
                id=node.element_id,  # Neo4j returns string IDs
                content=node["content"],
                sector=node["sector"],
                source=node["source"],
                salience=node["salience"],
                created_at=datetime.fromisoformat(node["created_at"]),
                valid_from=datetime.fromisoformat(node["valid_from"]),
                valid_to=None
            )
    raise RuntimeError("Failed to create bubble")
```

**Key Concepts:**
- **MERGE**: Idempotent operation - creates if doesn't exist, updates if exists
- **ON CREATE vs ON MATCH**: Different actions based on whether node existed
- **Temporal tracking**: `created_at` set once, `accessed_at` updated on access
- **Validity windows**: `valid_from` and `valid_to` for audit trails

### Search with CONTAINS and Limit

**File:** `src/database/queries.py:67-105`

```python
async def search_bubbles(query: str, limit: int = 10) -> list[BubbleResponse]:
    """
    Search for bubbles containing the query string.

    Uses CONTAINS for case-insensitive partial matching.
    Returns results ordered by recency (most recent first).
    """
    conn = await get_connection()

    cypher = """
    MATCH (b:Bubble)
    WHERE b.content CONTAINS $search_query
    AND b.valid_to IS NULL
    RETURN b
    ORDER BY b.created_at DESC
    LIMIT $result_limit
    """

    async with conn.session() as session:
        result = await session.run(
            cypher,
            search_query=query,      # Note: parameter renamed to avoid conflict
            result_limit=limit       # with session.run()'s positional args
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
        return bubbles
```

**Bug Fixed:** Parameter names (`$search_query`, `$result_limit`) differ from function arguments to avoid conflict with `session.run()`'s positional `query` parameter.

**Key Concepts:**
- **CONTAINS**: Case-insensitive substring matching
- **Valid-to filtering**: Only returns active (non-deleted) records
- **ORDER BY DESC**: Most recent first
- **LIMIT**: Prevents unbounded result sets

---

## 4. Pydantic Validation

### Request Schema with Field Validators

**File:** `src/utils/schemas.py:10-26`

```python
from pydantic import BaseModel, Field, field_validator


class BubbleCreate(BaseModel):
    """Schema for creating a new memory bubble."""
    content: str = Field(..., min_length=1, description="The memory content")
    sector: str = Field(..., description="Cognitive sector")
    source: str = Field(default="direct_chat", description="Origin of the data")
    salience: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: str) -> str:
        """Validate that sector is one of the five cognitive sectors."""
        valid_sectors = {"Episodic", "Semantic", "Procedural", "Emotional", "Reflective"}
        v_capitalized = v.capitalize()
        if v_capitalized not in valid_sectors:
            raise ValueError(f"sector must be one of: {', '.join(valid_sectors)}")
        return v_capitalized
```

**Key Concepts:**
- **Required fields**: `...` means field is required
- **Defaults**: `default=` provides fallback value
- **Constraints**: `ge` (greater than or equal), `le` (less than or equal)
- **Validators**: Custom validation logic with `@field_validator`
- **Normalization**: `.capitalize()` ensures consistent casing

### Response Schema with String IDs

**File:** `src/utils/schemas.py:28-42`

```python
class BubbleResponse(BaseModel):
    """Schema for a memory bubble response from the database.

    Note: Neo4j element_id is returned as a string (e.g., '4:uuid:0').
    """
    id: str  # Changed from int after discovering Neo4j format
    content: str
    sector: str
    source: str
    salience: float
    created_at: datetime
    valid_from: datetime
    valid_to: Optional[datetime] = None

    model_config = {"from_attributes": True}
```

**Important:** The `id` field must be `str`, not `int`. Neo4j's `element_id` returns a string like `'4:e087e584-a2bb-446e-9147-50a7b3f906df:0'`.

---

## 5. FastMCP Tool Definition

### Tool with Pydantic Field Descriptions

**File:** `src/tools/memory_tools.py:36-73`

```python
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Brain OS")


@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    sector: str = Field(description="Cognitive sector: Episodic, Semantic, Procedural, Emotional, or Reflective"),
    source: str = Field(default="direct_chat", description="Origin of the data"),
    salience: float = Field(default=0.5, description="Importance score from 0.0 to 1.0"),
) -> str:
    """
    Store a new memory in the Synaptic Graph.

    Creates a Bubble node with automatic timestamp tracking.
    Use this to preserve important context across sessions.
    """
    try:
        BubbleCreate = _get_schemas()
        upsert_bubble, _ = _get_queries()

        # Validate and create the bubble
        bubble_data = BubbleCreate(
            content=content,
            sector=sector,
            source=source,
            salience=salience
        )
        result = await upsert_bubble(bubble_data)

        return (
            f"Memory stored successfully!\n"
            f"- ID: {result.id}\n"
            f"- Sector: {result.sector}\n"
            f"- Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"- Salience: {result.salience}\n"
            f"- Content: {result.content[:100]}{'...' if len(result.content) > 100 else ''}"
        )
    except Exception as e:
        logger.error(f"Failed to create memory: {e}")
        return f"Error storing memory: {str(e)}"
```

**Key Concepts:**
- **Pydantic Fields**: Using `Field()` provides descriptions for LLM understanding
- **Default values**: Optional parameters have sensible defaults
- **Docstrings**: Tool description helps LLM understand when to use it
- **Error handling**: Catch exceptions and return user-friendly error messages
- **Lazy imports**: `_get_schemas()` and `_get_queries()` avoid circular imports

### Lazy Import Pattern

**File:** `src/tools/memory_tools.py:24-34`

```python
def _get_queries():
    """Lazy import queries to avoid startup issues."""
    from src.database.queries import upsert_bubble, search_bubbles
    return upsert_bubble, search_bubbles


def _get_schemas():
    """Lazy import schemas to avoid startup issues."""
    from src.utils.schemas import BubbleCreate
    return BubbleCreate
```

**Why lazy imports?** MCP tools are loaded at module import time. Direct imports at module level can cause circular dependencies or initialization order issues.

---

## 6. Claude Desktop Entry Point

### Root-Level Server with Path Handling

**File:** `brainos_server.py:1-70`

```python
"""
Brain OS MCP Server
Entry point for FastMCP CLI with proper path handling.
"""

import sys
from pathlib import Path

# Add project root to Python path BEFORE any imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import FastMCP and tools
from fastmcp import FastMCP
from pydantic import Field

# Import with lazy loading to avoid startup issues
def _get_queries():
    from src.database.queries import upsert_bubble, search_bubbles
    return upsert_bubble, search_bubbles

def _get_schemas():
    from src.utils.schemas import BubbleCreate
    return BubbleCreate

# Create FastMCP instance
mcp = FastMCP("Brain OS")

@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    sector: str = Field(description="Cognitive sector: Episodic, Semantic, Procedural, Emotional, or Reflective"),
    source: str = Field(default="direct_chat", description="Origin of the data"),
    salience: float = Field(default=0.5, description="Importance score from 0.0 to 1.0"),
) -> str:
    """Store a new memory in the Synaptic Graph."""
    try:
        BubbleCreate = _get_schemas()
        upsert_bubble, _ = _get_queries()
        bubble_data = BubbleCreate(content=content, sector=sector, source=source, salience=salience)
        result = await upsert_bubble(bubble_data)
        return f"Memory stored! ID: {result.id}, Sector: {result.sector}, Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool
async def get_memory(query: str = Field(description="Search term"), limit: int = Field(default=10)) -> str:
    """Retrieve memories from the Synaptic Graph."""
    try:
        _, search_bubbles = _get_queries()
        results = await search_bubbles(query, limit)
        if not results:
            return f"No memories found for '{query}'"
        output = [f"Found {len(results)} memories:\n"]
        for i, b in enumerate(results, 1):
            output.append(f"{i}. [{b.sector}] {b.content[:80]}...")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool
async def list_sectors() -> str:
    """List all cognitive sectors."""
    return """Brain OS Five-Sector Ontology:
- Episodic: Events and experiences
- Semantic: Hard facts and knowledge
- Procedural: Habits and workflows
- Emotional: Sentiment and vibe
- Reflective: Meta-memory"""
```

**Key Design Decisions:**
- **Root-level file**: Avoids relative path resolution issues in Claude Desktop
- **Path manipulation**: `sys.path.insert(0, ...)` ensures imports work correctly
- **Lazy imports**: Database modules imported inside functions, not at module level
- **Self-contained**: All tools defined in one file for easy CLI targeting

---

## Summary: Phase 1 Patterns

| Pattern | Purpose | File |
|---------|---------|------|
| Frozen dataclass config | Immutable, validated configuration | `src/core/config.py` |
| Async connection singleton | Single driver with connection pooling | `src/database/connection.py` |
| MERGE upsert | Idempotent create-or-update operations | `src/database/queries.py` |
| Pydantic validation | Type-safe request/response schemas | `src/utils/schemas.py` |
| FastMCP tools | LLM-callable functions with metadata | `src/tools/memory_tools.py` |
| Root entry point | Claude Desktop path resolution | `brainos_server.py` |

These patterns establish the foundation for Phase 2, where we'll add PocketFlow workflows, salience scoring, and multi-agent orchestration.
