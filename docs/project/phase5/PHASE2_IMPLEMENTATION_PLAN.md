# Phase 5 - Phase 2: Obsidian Bidirectional Sync - Implementation Plan

**Date**: 2026-01-13
**Status**: Ready for Implementation
**Scope**: Cron job syncs Obsidian → Neo4j every 15 minutes + bulk export

---

## Executive Summary

Phase 5.2 enables bidirectional synchronization between Obsidian and Neo4j. Users can edit memory files in Obsidian, and a background cron job automatically syncs changes back to Neo4j every 15 minutes. Also includes tools to bulk export existing Neo4j memories to Obsidian.

This is achieved by:

1. Creating an Obsidian file parser to extract structured data from markdown files
2. Implementing change detection to identify modified files
3. Creating background task for periodic sync (every 15 minutes)
4. Implementing conflict resolution (newest timestamp wins)
5. Adding bulk export tool for historical memories
6. Creating manual sync trigger tool

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│  Obsidian Vault │     │     Neo4j       │
│  (Local Files)  │◀────▶│   (Database)    │
└────────┬────────┘     └────────┬────────┘
         │                      │
         │ 1. File changed      │
         │ 2. Cron detects     │
         ▼                      │
    ┌─────────┐                  │
    │ Parser  │                  │
    └────┬────┘                  │
         │                       │
         │ 3. Extract data       │
         ▼                       │
    ┌─────────────────┐          │
    │  Sync Function  │──────────┘
    │  (Compare times)│
    └─────────────────┘
         │
         │ 4. Update Neo4j
         ▼
    ┌─────────────────┐
    │  Updated Bubble│
    └─────────────────┘
```

---

## Implementation Steps

### Step 1: Create Obsidian Parser (1-2 hours)

**File**: `src/utils/obsidian_parser.py`

```python
"""
Obsidian entity file parser.
Extracts structured data from markdown files with YAML frontmatter.

Phase 5.2: Bidirectional sync
"""

import logging
import re
import yaml
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_obsidian_entity(file_path: str) -> dict:
    """
    Parse Obsidian entity file into structured data.

    Args:
        file_path: Path to Obsidian markdown file

    Returns:
        Dict with keys: neo4j_id, entityType, salience, memory_type,
                     source, created, updated, observations, content

    Raises:
        ValueError: If file has no YAML frontmatter
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file
    content = file_path.read_text(encoding='utf-8')

    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError(f"No YAML frontmatter found in {file_path}")

    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    markdown_body = frontmatter_match.group(2)

    # Extract observations
    observations = []
    observations_match = re.search(r'## Observations\n(.*?)(?=\n##|\Z)', markdown_body, re.DOTALL)
    if observations_match:
        obs_text = observations_match.group(1).strip()
        observations = [
            line.strip('- ').strip()
            for line in obs_text.split('\n')
            if line.strip().startswith('-')
        ]

    # Extract title from first heading or filename
    title_match = re.search(r'^# (.+)$', markdown_body, re.MULTILINE)
    if title_match:
        content = title_match.group(1)
    else:
        content = file_path.stem  # Use filename as fallback

    return {
        "neo4j_id": frontmatter.get("neo4j_id"),
        "entityType": frontmatter.get("entityType"),
        "salience": frontmatter.get("salience"),
        "memory_type": frontmatter.get("memory_type"),
        "source": frontmatter.get("source"),
        "created": frontmatter.get("created"),
        "updated": frontmatter.get("updated"),
        "observations": observations,
        "content": content,
        "file_path": str(file_path)
    }
```

---

### Step 2: Create Sync Utilities (1-2 hours)

**File**: `src/utils/obsidian_sync.py`

```python
"""
Obsidian sync utilities.
Detects changed files and manages sync state.

Phase 5.2: Bidirectional sync
"""

import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# State file for last sync timestamp
LAST_SYNC_FILE = Path("data/last_obsidian_sync.txt")


def get_last_sync_time() -> datetime:
    """Get last sync timestamp from state file."""
    if LAST_SYNC_FILE.exists():
        try:
            return datetime.fromisoformat(LAST_SYNC_FILE.read_text().strip())
        except Exception as e:
            logger.warning(f"Failed to parse last sync time: {e}")

    # Default: 1 hour ago
    return datetime.now() - timedelta(hours=1)


def save_last_sync_time(timestamp: datetime) -> None:
    """Save last sync timestamp to state file."""
    LAST_SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_SYNC_FILE.write_text(timestamp.isoformat())
    logger.info(f"Updated last sync time: {timestamp.isoformat()}")


def get_changed_entities(vault_path: str, since: datetime) -> list[str]:
    """
    Get list of entity files modified since timestamp.

    Args:
        vault_path: Path to Obsidian vault
        since: Only return files modified after this time

    Returns:
        List of file paths for changed files
    """
    vault = Path(vault_path)
    if not vault.exists():
        logger.warning(f"Vault path not found: {vault_path}")
        return []

    changed_files = []

    # Scan for markdown files
    for file_path in vault.rglob("*.md"):
        # Skip .obsidian directory
        if ".obsidian" in str(file_path):
            continue

        # Check modified time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if mtime > since:
            changed_files.append(str(file_path))
            logger.debug(f"Changed file: {file_path.name} (modified: {mtime})")

    logger.info(f"Found {len(changed_files)} changed files since {since}")
    return changed_files


def resolve_conflict(neo4j_time: datetime, obsidian_time: datetime, entity_id: str) -> str:
    """
    Determine which version wins in conflict.

    Args:
        neo4j_time: Last access time from Neo4j
        obsidian_time: Updated time from Obsidian
        entity_id: Entity ID for logging

    Returns:
        "neo4j" | "obsidian" | "no_conflict"
    """
    if neo4j_time > obsidian_time:
        delta = (neo4j_time - obsidian_time).total_seconds()
        logger.warning(f"Conflict for {entity_id}: Neo4j newer by {delta}s")
        return "neo4j"
    elif obsidian_time > neo4j_time:
        delta = (obsidian_time - neo4j_time).total_seconds()
        logger.info(f"Syncing {entity_id}: Obsidian newer by {delta}s")
        return "obsidian"
    else:
        logger.debug(f"No conflict for {entity_id}: timestamps equal")
        return "no_conflict"
```

---

### Step 3: Add Neo4j Update Function (1-2 hours)

**File**: `src/database/queries/memory.py` (add new function)

```python
async def update_bubble_from_obsidian(
    neo4j_id: str,
    observations: list[str],
    salience: float = None
) -> bool:
    """
    Update Neo4j bubble with changes from Obsidian.

    Args:
        neo4j_id: Bubble ID from Obsidian frontmatter
        observations: Updated observations list
        salience: Updated salience (optional)

    Returns:
        True if updated, False if skipped (conflict) or not found
    """
    from src.database.connection import get_driver
    from datetime import datetime

    driver = get_driver()

    async with driver.session() as session:
        # Fetch current bubble
        result = await session.run("""
            MATCH (b:Bubble {id: $bubble_id})
            WHERE b.valid_to IS NULL
            RETURN b, b.last_accessed as last_accessed, b.created_at as created_at
        """, {"bubble_id": neo4j_id})

        record = result.single()
        if not record:
            logger.warning(f"Bubble {neo4j_id} not found in Neo4j")
            return False

        bubble = record["b"]
        neo4j_time = record["last_accessed"] or record["created_at"]

        # Conflict resolution would happen before this function
        # This function applies the update

        # Build SET clause dynamically
        set_clauses = ["b.last_accessed = $last_accessed"]
        params = {"bubble_id": neo4j_id, "last_accessed": datetime.now()}

        if observations is not None:
            set_clauses.append("b.observations = $observations")
            params["observations"] = observations

        if salience is not None:
            set_clauses.append("b.salience = $salience")
            params["salience"] = salience

        # Update bubble
        await session.run(f"""
            MATCH (b:Bubble {{id: $bubble_id}})
            WHERE b.valid_to IS NULL
            SET {', '.join(set_clauses)}
            RETURN b
        """, params)

        logger.info(f"Updated bubble {neo4j_id} from Obsidian")
        return True
```

---

### Step 4: Create Sync Function (1-2 hours)

**File**: `src/tasks/obsidian_sync.py`

```python
"""
Obsidian sync tasks.
Background cron job for bidirectional sync.

Phase 5.2: Bidirectional sync
"""

import asyncio
import logging
import os
from datetime import datetime

from src.utils.obsidian_parser import parse_obsidian_entity
from src.utils.obsidian_sync import (
    get_last_sync_time,
    save_last_sync_time,
    get_changed_entities,
    resolve_conflict
)
from src.database.queries.memory import get_bubble_by_id, update_bubble_from_obsidian

logger = logging.getLogger(__name__)


async def sync_obsidian_to_neo4j() -> dict:
    """
    Sync Obsidian changes to Neo4j.

    Returns:
        Dict with sync stats: synced, skipped, errors
    """
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "brain-os-vault")
    last_sync = get_last_sync_time()

    logger.info(f"Starting Obsidian sync (vault: {vault_path}, since: {last_sync})")

    # Get changed files
    changed_files = get_changed_entities(vault_path, last_sync)

    synced = 0
    skipped = 0
    errors = 0

    for file_path in changed_files:
        try:
            # Parse Obsidian file
            entity_data = parse_obsidian_entity(file_path)

            if not entity_data.get("neo4j_id"):
                logger.warning(f"File {file_path} has no neo4j_id, skipping")
                skipped += 1
                continue

            # Get Neo4j bubble for comparison
            bubble = await get_bubble_by_id(entity_data["neo4j_id"])
            if not bubble:
                logger.warning(f"Bubble {entity_data['neo4j_id']} not found, skipping")
                skipped += 1
                continue

            # Resolve conflict (compare timestamps)
            obsidian_time = datetime.fromisoformat(entity_data["updated"])
            neo4j_time = bubble.last_accessed or bubble.created_at

            resolution = resolve_conflict(neo4j_time, obsidian_time, entity_data["neo4j_id"])

            if resolution == "neo4j":
                skipped += 1
                continue

            # Update Neo4j
            updated = await update_bubble_from_obsidian(
                neo4j_id=entity_data["neo4j_id"],
                observations=entity_data["observations"],
                salience=entity_data.get("salience")
            )

            if updated:
                synced += 1
            else:
                skipped += 1

        except Exception as e:
            logger.error(f"Failed to sync {file_path}: {e}")
            errors += 1

    # Save last sync time
    save_last_sync_time(datetime.now())

    logger.info(f"Sync complete: {synced} synced, {skipped} skipped, {errors} errors")

    return {
        "synced": synced,
        "skipped": skipped,
        "errors": errors
    }
```

---

### Step 5: Add Background Task to Server (1 hour)

**File**: `brainos_server.py` (modify)

Add to startup:

```python
from src.tasks.obsidian_sync import sync_obsidian_to_neo4j

@mcp.on_startup
async def start_obsidian_sync_task():
    """Start background Obsidian sync task."""
    interval_minutes = int(os.getenv("OBSIDIAN_SYNC_INTERVAL_MINUTES", "15"))

    if interval_minutes <= 0:
        logger.info("Obsidian sync task disabled (interval <= 0)")
        return

    async def sync_loop():
        while True:
            await asyncio.sleep(interval_minutes * 60)
            try:
                await sync_obsidian_to_neo4j()
            except Exception as e:
                logger.error(f"Obsidian sync task error: {e}")

    asyncio.create_task(sync_loop())
    logger.info(f"Obsidian sync task started (interval: {interval_minutes} minutes)")
```

---

### Step 6: Create Bulk Export Tool (2-3 hours)

**File**: `src/tools/memory/bulk_export.py`

```python
"""
Bulk export memories to Obsidian.
Phase 5.2: Bidirectional sync
"""

import logging
from pydantic import Field

from src.database.queries.memory import get_all_bubbles
from src.utils.obsidian_client import sync_to_obsidian
from src.utils.entity_naming import generate_entity_name

logger = logging.getLogger(__name__)


def register_bulk_export(mcp) -> None:
    """Register bulk export tools with FastMCP."""

    @mcp.tool
    async def export_all_memories_to_obsidian(
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of memories to export"
        )
    ) -> str:
        """
        Bulk export existing Neo4j memories to Obsidian vault.

        Exports all valid bubbles to Obsidian as entity files.
        Skips memories that already exist in Obsidian.

        Best used after first setting up Obsidian to populate
        your vault with historical memories.
        """
        logger.info(f"Starting bulk export (limit: {limit})")

        # Fetch all bubbles
        bubbles = await get_all_bubbles(limit=limit)

        exported = 0
        skipped = 0
        errors = 0

        for i, bubble in enumerate(bubbles):
            try:
                # Generate entity name
                entity_name = generate_entity_name(
                    content=bubble.content,
                    entities=bubble.entities or [],
                    sector=bubble.sector
                )

                # Sync to Obsidian
                success = await sync_to_obsidian(
                    entity_name=entity_name,
                    entity_type=bubble.sector,
                    content=bubble.content,
                    observations=bubble.observations or [],
                    metadata={
                        "salience": bubble.salience,
                        "memory_type": bubble.memory_type,
                        "neo4j_id": str(bubble.id),
                        "created": bubble.created_at.isoformat(),
                        "source": bubble.source,
                        "sector": bubble.sector,
                    }
                )

                if success:
                    exported += 1
                else:
                    # Assume already exists or sync failed
                    skipped += 1

                # Progress logging every 10
                if (i + 1) % 10 == 0:
                    logger.info(f"Exported {i + 1}/{len(bubbles)} memories")

            except Exception as e:
                logger.error(f"Failed to export {bubble.id}: {e}")
                errors += 1

        logger.info(f"Bulk export complete: {exported} exported, {skipped} skipped, {errors} errors")

        return f"""
✅ Bulk export complete:
- Exported: {exported}
- Skipped (already exists or failed): {skipped}
- Errors: {errors}
- Total processed: {len(bubbles)}
"""
```

---

### Step 7: Create Manual Sync Tool (30 minutes)

**File**: `src/tools/obsidian/sync_now.py`

```python
"""
Manual Obsidian sync tools.
Phase 5.2: Bidirectional sync
"""

import logging
from pydantic import Field

from src.tasks.obsidian_sync import sync_obsidian_to_neo4j

logger = logging.getLogger(__name__)


def register_sync_tools(mcp) -> None:
    """Register manual sync tools with FastMCP."""

    @mcp.tool
    async def sync_obsidian_now() -> str:
        """
        Manually trigger Obsidian → Neo4j sync immediately.

        Use this to sync changes from Obsidian without waiting
        for the next scheduled cron job (every 15 minutes).

        Automatically detects changed files and updates Neo4j.
        """
        logger.info("Manual Obsidian sync triggered")

        result = await sync_obsidian_to_neo4j()

        return f"""
✅ Manual sync complete:
- Synced: {result['synced']}
- Skipped: {result['skipped']}
- Errors: {result['errors']}

Next scheduled sync: in {os.getenv('OBSIDIAN_SYNC_INTERVAL_MINUTES', '15')} minutes
"""
```

---

### Step 8: Update Tool Registration (15 minutes)

**File**: `src/tools/__init__.py`

```python
from src.tools.obsidian.sync_now import register_sync_tools

def register_all_tools(mcp) -> None:
    # ... existing imports ...

    # Phase 5.2: Obsidian sync tools
    from src.tools.memory.bulk_export import register_bulk_export
    register_bulk_export(mcp)
    register_sync_tools(mcp)
```

---

### Step 9: Update Dependencies (5 minutes)

**File**: `pyproject.toml`

```toml
dependencies = [
    # ... existing ...
    "PyYAML>=6.0.0",
]
```

---

### Step 10: Testing (2-3 hours)

**Unit Tests** - `tests/unit/test_obsidian_parser.py`

```python
import pytest
from src.utils.obsidian_parser import parse_obsidian_entity
from pathlib import Path

def test_parse_valid_file():
    """Test parsing valid Obsidian entity file."""
    # Create test file
    test_file = Path("/tmp/test_entity.md")
    test_file.write_text("""---
entityType: Semantic
salience: 0.8
neo4j_id: test-id-123
created: '2026-01-13'
updated: '2026-01-13'
---

# Test Entity

## Observations
- Test observation 1
- Test observation 2
""")

    result = parse_obsidian_entity(str(test_file))

    assert result["entityType"] == "Semantic"
    assert result["salience"] == 0.8
    assert result["neo4j_id"] == "test-id-123"
    assert len(result["observations"]) == 2
    assert result["content"] == "Test Entity"
```

**Integration Test** - `tests/integration/test_obsidian_sync.py`

```python
import pytest
from src.tasks.obsidian_sync import sync_obsidian_to_neo4j

@pytest.mark.asyncio
async def test_obsidian_sync():
    """Test bidirectional sync."""
    result = await sync_obsidian_to_neo4j()

    assert "synced" in result
    assert isinstance(result["synced"], int)
```

---

## Success Criteria

Phase 5.2 is complete when:

- ✅ `sync_obsidian_now()` tool available and working
- ✅ `export_all_memories_to_obsidian()` tool available and working
- ✅ Background cron job runs every 15 minutes
- ✅ Edit Obsidian file → Neo4j updates within 15 minutes
- ✅ Conflict resolution works (newest wins)
- ✅ Bulk export can export 50+ memories
- ✅ All unit tests passing
- ✅ Graceful degradation if Obsidian unavailable

---

## Files Summary

| File | Action | Lines |
|------|--------|-------|
| `src/utils/obsidian_parser.py` | New | ~100 |
| `src/utils/obsidian_sync.py` | New | ~80 |
| `src/database/queries/memory.py` | Modify | +50 |
| `src/tasks/obsidian_sync.py` | New | ~60 |
| `src/tools/memory/bulk_export.py` | New | ~70 |
| `src/tools/obsidian/sync_now.py` | New | ~40 |
| `brainos_server.py` | Modify | +15 |
| `tests/unit/test_obsidian_parser.py` | New | ~80 |
| `tests/integration/test_obsidian_sync.py` | New | ~60 |

**Total**: ~555 lines added across 9 files

---

## Next Steps

1. **User approves this plan**
2. **Implement Step 1-10** in order
3. **Test locally** with Obsidian
4. **Verify bulk export** with existing memories
5. **Move to Phase 5.3**: Voice memo processing

---

**Status**: Ready for implementation upon user approval
**Estimated Time**: 12-15 hours (1.5-2 days)
**Complexity**: Medium (requires file I/O, cron jobs, conflict resolution)
