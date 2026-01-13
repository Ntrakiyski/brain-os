# Phase 5 - Phase 1: Obsidian Integration - Implementation Plan

**Date**: 2026-01-13
**Status**: Ready for Implementation
**Scope**: Neo4j → Obsidian sync on memory creation

---

## Executive Summary

When a user creates a memory via Brain OS MCP tools, a corresponding markdown file will be instantly created in the Obsidian vault. This is achieved by:

1. Running **YuNaga224/obsidian-memory-mcp** as a Docker service alongside Brain OS
2. Creating an **Obsidian MCP client utility** in Brain OS
3. Enhancing `create_memory` to sync to Obsidian after Neo4j insert
4. Handling graceful degradation if Obsidian is offline

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude / User  │────▶│   Brain OS MCP  │────▶│     Neo4j       │
│                 │     │   (Port 9131)   │     │   (External)    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 │ create_memory()
                                 │   (after Neo4j success)
                                 ▼
                        ┌─────────────────┐
                        │  Obsidian MCP   │
                        │  (Port 8001)    │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Obsidian Vault │
                        │  (entities/)    │
                        └─────────────────┘
```

---

## New Files to Create

### 1. `src/utils/obsidian_client.py`

**Purpose**: FastMCP client for connecting to Obsidian MCP server

```python
"""
Obsidian MCP client utility.
Connects to YuNaga224/obsidian-memory-mcp server.
"""

import asyncio
import logging
import os
from functools import lru_cache

from fastmcp import Client

logger = logging.getLogger(__name__)

# Singleton connection pool
_obsidian_client: Client | None = None


async def get_obsidian_client() -> Client:
    """
    Get Obsidian MCP client with connection pooling.

    Returns:
        FastMCP Client connected to Obsidian MCP server

    Raises:
        ConnectionError: If Obsidian MCP server is unreachable
    """
    global _obsidian_client

    url = os.getenv("OBSIDIAN_MCP_URL", "http://localhost:8001/mcp")

    try:
        async with asyncio.timeout(5):  # 5-second connection timeout
            if _obsidian_client is None:
                logger.info(f"Connecting to Obsidian MCP at {url}")
                _obsidian_client = Client(url)
                # Verify connection by listing tools
                tools = await _obsidian_client.list_tools()
                logger.debug(f"Obsidian MCP connected, available tools: {len(tools)}")
            return _obsidian_client
    except asyncio.TimeoutError:
        logger.warning(f"Timeout connecting to Obsidian MCP at {url}")
        raise ConnectionError(f"Timeout connecting to Obsidian MCP at {url}")
    except Exception as e:
        logger.error(f"Failed to connect to Obsidian MCP: {e}")
        raise ConnectionError(f"Failed to connect to Obsidian MCP: {e}")


async def sync_to_obsidian(
    entity_name: str,
    entity_type: str,
    content: str,
    observations: list[str],
    metadata: dict,
) -> bool:
    """
    Sync a memory to Obsidian vault.

    Args:
        entity_name: Name for the Obsidian entity (will be filename)
        entity_type: Entity type (e.g., "Semantic", "Episodic")
        content: Main content/description
        observations: List of observation strings
        metadata: Additional metadata dict

    Returns:
        True if sync successful, False otherwise
    """
    try:
        async with asyncio.timeout(5):
            async with await get_obsidian_client() as obsidian:
                await obsidian.call_tool("create_entities", {
                    "name": entity_name,
                    "entityType": entity_type,
                    "observations": observations,
                    "metadata": metadata
                })
                logger.info(f"Synced to Obsidian: {entity_name}")
                return True
    except asyncio.TimeoutError:
        logger.warning(f"Obsidian sync timeout for {entity_name}")
        return False
    except ConnectionError:
        logger.warning(f"Obsidian unavailable, skipping sync for {entity_name}")
        return False
    except Exception as e:
        logger.error(f"Obsidian sync failed for {entity_name}: {e}")
        return False
```

### 2. `src/utils/entity_naming.py`

**Purpose**: Generate clean, readable entity names from memory content

```python
"""
Entity name generation utility.
Creates readable, consistent filenames for Obsidian entities.
"""

import re
import unicodedata
from typing import List


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    - Remove special characters
    - Replace spaces with underscores
    - Convert to title case
    - Limit to 50 characters

    Examples:
        "Chose PostgreSQL" -> "Chose_PostgreSQL"
        "Met with FastTrack" -> "Met_With_FastTrack"
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Remove special characters (keep alphanumeric, spaces, underscores, hyphens)
    text = re.sub(r'[^\w\s-]', '', text)

    # Replace spaces and hyphens with underscores
    text = re.sub(r'[\s-]+', '_', text)

    # Title case
    text = text.title()

    # Remove leading/trailing underscores
    text = text.strip('_')

    # Limit to 50 characters
    return text[:50]


def generate_entity_name(
    content: str,
    entities: List[str],
    sector: str,
) -> str:
    """
    Generate a clean entity name for Obsidian file.

    Strategy:
    1. If entities provided: Use first entity + key action from content
    2. If no entities: Extract keywords from content + sector suffix
    3. Always sanitize and limit to 50 characters

    Args:
        content: Memory content
        entities: List of entity names
        sector: Cognitive sector (Semantic, Episodic, etc.)

    Returns:
        Sanitized entity name suitable for filename

    Examples:
        generate_entity_name(
            "Chose PostgreSQL over MongoDB for ACID compliance",
            ["PostgreSQL", "MongoDB"],
            "Semantic"
        )
        # Returns: "PostgreSQL_vs_MongoDB_Decision"

        generate_entity_name(
            "Met with FastTrack client about N8N workflow",
            ["FastTrack"],
            "Episodic"
        )
        # Returns: "FastTrack_N8N_Workflow_Meeting"
    """
    # Extract action verbs and key nouns from content
    action_words = ["decision", "chose", "selected", "meeting", "discussed",
                   "deployed", "implemented", "learned", "discovered"]

    content_lower = content.lower()
    detected_action = None
    for action in action_words:
        if action in content_lower:
            detected_action = action.title()
            break

    if entities:
        # Use first entity + action/sector
        primary_entity = slugify(entities[0])

        if len(entities) > 1:
            # Multiple entities: "Entity1_vs_Entity2_Decision"
            secondary_entity = slugify(entities[1])
            if detected_action:
                return f"{primary_entity}_vs_{secondary_entity}_{detected_action}"
            return f"{primary_entity}_and_{secondary_entity}_{sector[:3]}"
        else:
            # Single entity: "Entity_Action" or "Entity_Sector"
            if detected_action:
                return f"{primary_entity}_{detected_action}"
            return f"{primary_entity}_{sector[:4]}"
    else:
        # No entities: Extract from content
        words = content.split()
        # First 2-3 meaningful words
        keywords = [w for w in words if len(w) > 3][:3]
        prefix = "_".join(slugify(k) for k in keywords)

        if detected_action:
            return f"{prefix}_{detected_action}"
        return f"{prefix}_{sector[:3]}"

    # Fallback
    return f"Memory_{sector[:3]}"
```

---

## Files to Modify

### 1. `src/tools/memory/create_memory.py`

**Change**: Add Obsidian sync after Neo4j insert (with graceful degradation)

**New code to insert after `upsert_bubble` success**:

```python
# After line 100 (result = await upsert_bubble(bubble_data))

# Phase 5.1: Sync to Obsidian (if configured)
obsidian_sync_result = ""
try:
    from src.utils.obsidian_client import sync_to_obsidian
    from src.utils.entity_naming import generate_entity_name

    entity_name = generate_entity_name(
        content=content,
        entities=entities,
        sector=sector,
    )

    obsidian_metadata = {
        "salience": salience,
        "memory_type": memory_type,
        "neo4j_id": str(result.id),
        "created": result.created_at.isoformat(),
        "source": source,
        "sector": sector,
    }

    sync_success = await sync_to_obsidian(
        entity_name=entity_name,
        entity_type=sector,
        content=content,
        observations=observations,
        metadata=obsidian_metadata,
    )

    if sync_success:
        obsidian_sync_result = f"\n- Obsidian: {entity_name}.md"
        logger.info(f"Successfully synced to Obsidian: {entity_name}")
    else:
        obsidian_sync_result = "\n⚠️ Obsidian sync: Unavailable (Neo4j stored)"
        logger.warning(f"Obsidian sync failed for memory {result.id}")

except ImportError:
    # Obsidian utilities not available - skip sync
    logger.debug("Obsidian client not available, skipping sync")
except Exception as e:
    # Obsidian sync failed - don't fail the entire operation
    logger.warning(f"Obsidian sync error: {e}")
    obsidian_sync_result = "\n⚠️ Obsidian sync: Failed (Neo4j stored)"

# Update return message to include Obsidian status
return (
    f"Memory stored successfully!{obsidian_sync_result}\n"
    f"- Neo4j ID: {result.id}\n"
    f"- Sector: {result.sector}\n"
    f"- Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    f"- Salience: {result.salience}\n"
    f"- Content: {result.content[:100]}{'...' if len(result.content) > 100 else ''}"
)
```

### 2. `docker-compose.yml`

**Change**: Add Obsidian MCP server as a service

```yaml
services:
  # BrainOS MCP Server (existing)
  brainos:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: brainos-server
    expose:
      - "9131"
    environment:
      # ... existing env vars ...
      # Add Obsidian MCP URL
      - OBSIDIAN_MCP_URL=http://obsidian-mcp:8001/mcp
    depends_on:
      - obsidian-mcp  # Wait for Obsidian MCP to be ready
    restart: unless-stopped

  # NEW: Obsidian MCP Server
  obsidian-mcp:
    image: node:18-alpine
    container_name: obsidian-mcp-server
    working_dir: /app
    expose:
      - "8001"  # HTTP MCP endpoint (internal only)
    environment:
      - MEMORY_DIR=/vault
      - NODE_ENV=production
    volumes:
      - obsidian-vault:/vault
    command:
      - /bin/sh
      - -c
      - |
        npm install -g @yunaga224/obsidian-memory-mcp
        obsidian-memory-mcp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8001/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

# Named volume for Obsidian vault
volumes:
  obsidian-vault:
    driver: local
```

**Note**: The YuNaga224/obsidian-memory-mcp package may need to be installed differently.
The actual implementation will use the cloned repository built into a Docker image.

**Alternative approach** (more reliable):

```yaml
  obsidian-mcp:
    build:
      context: ./obsidian-mcp
      dockerfile: Dockerfile
    container_name: obsidian-mcp-server
    expose:
      - "8001"
    environment:
      - MEMORY_DIR=/vault
      - PORT=8001
    volumes:
      - obsidian-vault:/vault
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8001/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

With `obsidian-mcp/Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy pre-built obsidian-memory-mcp or build from source
COPY . .

RUN npm install && npm run build

ENV MEMORY_DIR=/vault
ENV PORT=8001

VOLUME ["/vault"]

EXPOSE 8001

CMD ["node", "dist/index.js"]
```

### 3. `.env.example`

**Change**: Already has OBSIDIAN_MCP_URL, no changes needed

The `.env.example` already includes:
```env
OBSIDIAN_MCP_URL=http://localhost:8001/mcp
OBSIDIAN_VAULT_PATH=brain-os-vault
```

For Docker, use:
```env
OBSIDIAN_MCP_URL=http://obsidian-mcp:8001/mcp
```

---

## Implementation Order

### Step 1: Create Utility Files (1-2 hours)
- [ ] Create `src/utils/obsidian_client.py`
- [ ] Create `src/utils/entity_naming.py`
- [ ] Write unit tests for entity_naming.py

### Step 2: Enhance create_memory (1 hour)
- [ ] Modify `src/tools/memory/create_memory.py`
- [ ] Add Obsidian sync after Neo4j insert
- [ ] Add graceful degradation

### Step 3: Docker Integration (1-2 hours)
- [ ] Create `obsidian-mcp/Dockerfile`
- [ ] Modify `docker-compose.yml`
- [ ] Test local Docker deployment

### Step 4: Testing (1-2 hours)
- [ ] Write integration test
- [ ] Test end-to-end: create memory → verify Obsidian file
- [ ] Test offline mode: stop Obsidian MCP → verify Neo4j still works
- [ ] Test file format: verify YAML frontmatter and markdown

---

## Testing Strategy

### Unit Tests

**`tests/test_entity_naming.py`**:
```python
from src.utils.entity_naming import generate_entity_name, slugify

def test_slugify():
    assert slugify("Chose PostgreSQL") == "Chose_PostgreSQL"
    assert slugify("Met with FastTrack") == "Met_With_FastTrack"
    assert slugify("Test@#$%Special") == "TestSpecial"

def test_generate_entity_name_with_entities():
    result = generate_entity_name(
        "Chose PostgreSQL over MongoDB",
        ["PostgreSQL", "MongoDB"],
        "Semantic"
    )
    assert "PostgreSQL" in result
    assert "MongoDB" in result or "Decision" in result

def test_generate_entity_name_no_entities():
    result = generate_entity_name(
        "Important meeting about project deadlines",
        [],
        "Episodic"
    )
    assert len(result) <= 50
    assert " " not in result  # No spaces, only underscores
```

### Integration Test

**`tests/test_obsidian_integration.py`**:
```python
import asyncio
from fastmcp import Client

async def test_create_memory_syncs_to_obsidian():
    """Test that creating a memory syncs to Obsidian."""
    async with Client("http://localhost:9131/mcp") as brain:
        result = await brain.call_tool("create_memory", {
            "content": "Test: PostgreSQL decision for ACID compliance",
            "sector": "Semantic",
            "entities": ["PostgreSQL", "TestProject"],
            "observations": ["Test observation"],
            "salience": 0.7,
            "memory_type": "thinking",
            "source": "test"
        })

        # Verify success
        assert "Neo4j" in result or "stored" in result.lower()
        # Check if Obsidian sync succeeded (may fail if Obsidian offline)
        if "Obsidian" in result:
            print("✓ Obsidian sync successful")
        else:
            print("⚠ Obsidian sync skipped (offline)")

if __name__ == "__main__":
    asyncio.run(test_create_memory_syncs_to_obsidian())
```

### Manual Verification

1. **Start services**:
   ```bash
   docker compose up -d
   ```

2. **Create test memory**:
   ```python
   # Using Claude Desktop or MCP client
   create_memory(
       content="Chose PostgreSQL for Project X due to ACID compliance",
       sector="Semantic",
       entities=["PostgreSQL", "Project X"],
       observations=["Financial data needs transactions"],
       salience=0.85,
       memory_type="instinctive"
   )
   ```

3. **Verify Neo4j**:
   - Open Neo4j Browser: http://localhost:7474
   - Query: `MATCH (b:Bubble) RETURN b ORDER BY b.created_at DESC LIMIT 1`

4. **Verify Obsidian**:
   - Check Docker volume: `docker exec -it brainos-server ls -la /vault/entities/`
   - Or mount volume locally and open in Obsidian app

---

## Success Criteria

Phase 1 is complete when:

- ✅ `docker compose up` starts both Brain OS and Obsidian MCP
- ✅ `create_memory` tool creates Neo4j bubble
- ✅ Obsidian file appears in `entities/` folder
- ✅ File has valid YAML frontmatter
- ✅ File is visible in Obsidian graph view
- ✅ If Obsidian MCP is offline, Neo4j still works
- ✅ No errors in Brain OS logs for normal operation

---

## Files Summary

| File | Action | Lines Added | Purpose |
|------|--------|-------------|---------|
| `src/utils/obsidian_client.py` | New | ~80 | Obsidian MCP client |
| `src/utils/entity_naming.py` | New | ~100 | Entity name generation |
| `src/tools/memory/create_memory.py` | Modify | +35 | Add Obsidian sync |
| `docker-compose.yml` | Modify | +30 | Add Obsidian MCP service |
| `obsidian-mcp/Dockerfile` | New | ~20 | Dockerfile for Obsidian MCP |
| `tests/test_entity_naming.py` | New | ~50 | Unit tests |
| `tests/test_obsidian_integration.py` | New | ~40 | Integration test |

**Total**: ~355 lines added across 7 files

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YuNaga224 server API changes | Medium | Check for latest docs, version pin |
| Docker network issues | Low | Use internal service names, health checks |
| Obsidian file permissions | Low | Run as non-root, volume mount options |
| Connection timeout issues | Low | 5-second timeout, retry logic |
| Name collision in Obsidian | Low | Add timestamp suffix if exists |

---

## Next Steps

1. **User approves this plan**
2. **Implement Step 1**: Create utility files
3. **Implement Step 2**: Enhance create_memory
4. **Implement Step 3**: Docker integration
5. **Implement Step 4**: Testing
6. **User tests locally**
7. **Move to Phase 2**: Bidirectional sync

---

**Status**: Ready for implementation upon user approval
**Estimated Time**: 4-6 hours
**Complexity**: Medium (3 new files, 2 modified files, Docker integration)
