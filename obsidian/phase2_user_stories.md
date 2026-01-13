# Phase 2: Bidirectional Sync & Bulk Operations
**Goal**: Cron job syncs Obsidian changes → Neo4j every 15 minutes + bulk export existing memories

---

## Overview

Phase 2 enables bidirectional synchronization between Obsidian and Neo4j. Users can edit memory files in Obsidian, and a background cron job automatically syncs changes back to Neo4j every 15 minutes. Also includes tools to bulk export existing Neo4j memories to Obsidian.

**Success Criteria**:
- ✅ Cron job runs every 15 minutes
- ✅ Detects Obsidian file changes (modified since last sync)
- ✅ Updates Neo4j bubbles with Obsidian changes
- ✅ Handles conflicts (Neo4j vs Obsidian timestamp comparison)
- ✅ Bulk export tool syncs 100+ existing memories to Obsidian
- ✅ Relationship creation between entities

**Out of Scope**:
- ❌ Voice memo processing (Phase 3)
- ❌ Daily notes automation (Phase 3)
- ❌ Advanced AI workflows (Phase 3)

---

## User Stories

### Story 1: Parse Obsidian Entity Files

**As a** Brain OS developer
**I want to** parse Obsidian markdown files into structured data
**So that** I can sync changes back to Neo4j

**Acceptance Criteria**:
- [ ] New function: `parse_obsidian_entity(file_path: str) -> dict`
- [ ] Extracts YAML frontmatter (entityType, salience, neo4j_id, etc.)
- [ ] Extracts markdown sections (Observations, Metadata)
- [ ] Handles missing sections gracefully
- [ ] Returns structured dict with all fields
- [ ] Unit tests for various file formats

**Technical Implementation**:
```python
# src/utils/obsidian_parser.py
import yaml
import re

def parse_obsidian_entity(file_path: str) -> dict:
    """Parse Obsidian entity file into structured data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError("No YAML frontmatter found")

    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    markdown_body = frontmatter_match.group(2)

    # Extract observations
    observations_match = re.search(r'## Observations\n(.*?)(?=\n##|\Z)', markdown_body, re.DOTALL)
    observations = []
    if observations_match:
        obs_text = observations_match.group(1).strip()
        observations = [line.strip('- ').strip() for line in obs_text.split('\n') if line.strip().startswith('-')]

    return {
        "neo4j_id": frontmatter.get("neo4j_id"),
        "entityType": frontmatter.get("entityType"),
        "salience": frontmatter.get("salience"),
        "memory_type": frontmatter.get("memory_type"),
        "source": frontmatter.get("source"),
        "created": frontmatter.get("created"),
        "updated": frontmatter.get("updated"),
        "observations": observations,
        "content": extract_title(markdown_body)
    }
```

---

### Story 2: Detect Changed Files in Obsidian Vault

**As a** Brain OS system
**I want to** detect which Obsidian files were modified since last sync
**So that** I only process changed files

**Acceptance Criteria**:
- [ ] New function: `get_changed_entities(vault_path: str, since: datetime) -> list[str]`
- [ ] Scans `entities/` directory recursively
- [ ] Compares file `mtime` (modified time) with `since` timestamp
- [ ] Returns list of file paths for changed files
- [ ] Ignores `.obsidian/` directory
- [ ] Logs number of changed files found

**Technical Implementation**:
```python
# src/utils/obsidian_sync.py
import os
from pathlib import Path
from datetime import datetime

def get_changed_entities(vault_path: str, since: datetime) -> list[str]:
    """Get list of entity files modified since timestamp."""
    changed_files = []
    entities_dir = Path(vault_path) / "entities"

    if not entities_dir.exists():
        return []

    for file_path in entities_dir.rglob("*.md"):
        # Skip .obsidian directory
        if ".obsidian" in str(file_path):
            continue

        # Check modified time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if mtime > since:
            changed_files.append(str(file_path))

    return changed_files
```

---

### Story 3: Update Neo4j Bubble from Obsidian Entity

**As a** Brain OS system
**I want to** update Neo4j bubbles with changes from Obsidian
**So that** manual edits in Obsidian are reflected in the database

**Acceptance Criteria**:
- [ ] New function: `update_bubble_from_obsidian(entity_data: dict) -> bool`
- [ ] Finds bubble by `neo4j_id` from frontmatter
- [ ] Updates fields: observations, salience (if changed)
- [ ] Sets `valid_to` on old version (audit trail)
- [ ] Creates new version with `valid_from = now()`
- [ ] Handles conflict: If Neo4j `updated_at` > Obsidian `updated`, skip (Neo4j wins)
- [ ] Returns True if updated, False if skipped

**Technical Implementation**:
```python
# src/database/queries/memory.py
async def update_bubble_from_obsidian(entity_data: dict) -> bool:
    """Update Neo4j bubble with Obsidian changes."""
    neo4j_id = entity_data["neo4j_id"]

    # Fetch current bubble
    bubble = await get_bubble_by_id(neo4j_id)
    if not bubble:
        logger.warning(f"Bubble {neo4j_id} not found in Neo4j")
        return False

    # Conflict resolution: Compare timestamps
    obsidian_updated = datetime.fromisoformat(entity_data["updated"])
    if bubble.last_accessed and bubble.last_accessed > obsidian_updated:
        logger.info(f"Neo4j newer than Obsidian for {neo4j_id}, skipping")
        return False

    # Update bubble
    async with get_driver().session() as session:
        result = await session.run("""
            MATCH (b:Bubble {id: $bubble_id})
            WHERE b.valid_to IS NULL
            SET
                b.valid_to = datetime(),
                b.observations = $observations,
                b.salience = $salience,
                b.last_accessed = datetime()
            RETURN b
        """, {
            "bubble_id": neo4j_id,
            "observations": entity_data["observations"],
            "salience": entity_data["salience"]
        })

        return result.single() is not None
```

---

### Story 4: Create Cron Job for Bidirectional Sync

**As a** Brain OS user
**I want** automatic sync from Obsidian to Neo4j every 15 minutes
**So that** my Obsidian edits are always reflected in Brain OS

**Acceptance Criteria**:
- [ ] FastMCP background task runs every 15 minutes
- [ ] Task calls `sync_obsidian_to_neo4j()` function
- [ ] Function:
  1. Gets last sync timestamp (stored in file or DB)
  2. Scans Obsidian vault for changed files
  3. Parses each changed file
  4. Updates corresponding Neo4j bubbles
  5. Updates last sync timestamp
  6. Logs summary: "{N} files synced, {M} skipped, {E} errors"
- [ ] Runs in background, doesn't block MCP server
- [ ] Configurable interval via env var: `OBSIDIAN_SYNC_INTERVAL_MINUTES` (default: 15)

**Technical Implementation**:
```python
# brainos_server.py (add background task)
from fastmcp import FastMCP
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

mcp = FastMCP("Brain OS")

# State file for last sync timestamp
LAST_SYNC_FILE = Path("/tmp/brainos_last_obsidian_sync.txt")

async def sync_obsidian_to_neo4j():
    """Sync Obsidian changes to Neo4j."""
    # Get last sync time
    if LAST_SYNC_FILE.exists():
        last_sync = datetime.fromisoformat(LAST_SYNC_FILE.read_text())
    else:
        last_sync = datetime.now() - timedelta(hours=1)  # Default: last hour

    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "/home/user/brain-os-vault")

    # Get changed files
    changed_files = get_changed_entities(vault_path, last_sync)
    logger.info(f"Found {len(changed_files)} changed files in Obsidian")

    synced = 0
    skipped = 0
    errors = 0

    for file_path in changed_files:
        try:
            entity_data = parse_obsidian_entity(file_path)
            updated = await update_bubble_from_obsidian(entity_data)
            if updated:
                synced += 1
            else:
                skipped += 1
        except Exception as e:
            logger.error(f"Failed to sync {file_path}: {e}")
            errors += 1

    # Update last sync timestamp
    LAST_SYNC_FILE.write_text(datetime.now().isoformat())

    logger.info(f"Obsidian sync complete: {synced} synced, {skipped} skipped, {errors} errors")

@mcp.on_startup
async def start_sync_task():
    """Start background sync task."""
    interval_minutes = int(os.getenv("OBSIDIAN_SYNC_INTERVAL_MINUTES", "15"))

    async def sync_loop():
        while True:
            await asyncio.sleep(interval_minutes * 60)
            try:
                await sync_obsidian_to_neo4j()
            except Exception as e:
                logger.error(f"Sync task error: {e}")

    asyncio.create_task(sync_loop())
    logger.info(f"Obsidian sync task started (interval: {interval_minutes} minutes)")
```

---

### Story 5: Handle Sync Conflicts

**As a** Brain OS developer
**I want** conflict resolution when both Neo4j and Obsidian have changes
**So that** data isn't lost or overwritten incorrectly

**Acceptance Criteria**:
- [ ] Conflict detection: Compare `last_accessed` (Neo4j) vs `updated` (Obsidian)
- [ ] Resolution strategy: **Newest wins** (latest timestamp)
- [ ] If Neo4j newer → skip Obsidian sync, log conflict
- [ ] If Obsidian newer → update Neo4j
- [ ] Conflict log file: `logs/obsidian_sync_conflicts.log`
- [ ] Log entry includes: file path, Neo4j timestamp, Obsidian timestamp, resolution

**Technical Implementation**:
```python
def resolve_conflict(bubble, entity_data) -> str:
    """Determine which version wins in conflict.

    Returns: "neo4j" | "obsidian" | "no_conflict"
    """
    neo4j_time = bubble.last_accessed or bubble.created_at
    obsidian_time = datetime.fromisoformat(entity_data["updated"])

    if neo4j_time > obsidian_time:
        logger.warning(f"Conflict for {bubble.id}: Neo4j newer ({neo4j_time} > {obsidian_time})")
        return "neo4j"
    elif obsidian_time > neo4j_time:
        logger.info(f"Syncing {bubble.id}: Obsidian newer ({obsidian_time} > {neo4j_time})")
        return "obsidian"
    else:
        return "no_conflict"
```

---

### Story 6: Bulk Export Existing Memories to Obsidian

**As a** Brain OS user
**I want** to export all existing Neo4j memories to Obsidian
**So that** I can browse historical memories in Obsidian

**Acceptance Criteria**:
- [ ] New tool: `export_all_memories_to_obsidian(limit: int = 100)`
- [ ] Fetches all valid bubbles from Neo4j (where `valid_to IS NULL`)
- [ ] For each bubble:
  1. Check if already exported (search Obsidian by neo4j_id)
  2. If exists, skip
  3. If not, create entity in Obsidian
- [ ] Processes in batches of 10 (avoid overwhelming Obsidian MCP)
- [ ] Returns summary: "{N} exported, {M} skipped, {E} errors"
- [ ] Progress logging every 10 bubbles

**Technical Implementation**:
```python
# src/tools/memory/bulk_export.py
@mcp.tool
async def export_all_memories_to_obsidian(
    limit: int = Field(default=100, description="Max memories to export")
) -> str:
    """Bulk export existing Neo4j memories to Obsidian vault."""

    # Fetch all bubbles
    bubbles = await get_all_bubbles(limit=limit)

    exported = 0
    skipped = 0
    errors = 0

    async with get_obsidian_client() as obsidian:
        for i, bubble in enumerate(bubbles):
            try:
                # Check if already exported
                existing = await obsidian.call_tool("search_nodes", {
                    "query": {"neo4j_id": bubble.id}
                })

                if existing:
                    skipped += 1
                    continue

                # Create entity
                entity_name = generate_entity_name(bubble.content, bubble.entities)
                await obsidian.call_tool("create_entities", {
                    "name": entity_name,
                    "entityType": bubble.sector,
                    "observations": bubble.observations,
                    "metadata": {
                        "neo4j_id": bubble.id,
                        "salience": bubble.salience,
                        "memory_type": bubble.memory_type,
                        "created": bubble.created_at.isoformat(),
                        "source": bubble.source
                    }
                })
                exported += 1

                # Progress logging
                if (i + 1) % 10 == 0:
                    logger.info(f"Exported {i + 1}/{len(bubbles)} memories")

            except Exception as e:
                logger.error(f"Failed to export {bubble.id}: {e}")
                errors += 1

    return f"""
    ✅ Bulk export complete:
    - Exported: {exported}
    - Skipped (already exists): {skipped}
    - Errors: {errors}
    """
```

---

### Story 7: Create Entity Relationships in Obsidian

**As a** Brain OS user
**I want** entity relationships visible in Obsidian graph view
**So that** I can explore connections between memories

**Acceptance Criteria**:
- [ ] When creating entity in Obsidian, also create relations
- [ ] Relations based on shared entities:
  - If 2 bubbles share entity "Project X" → create relation
- [ ] Relation labels:
  - `Related To` (generic)
  - `Same Project` (if share project entity)
  - `Same Technology` (if share tech entity)
- [ ] Use YuNaga224 `create_relations` tool
- [ ] Visible in Obsidian graph view as edges

**Technical Implementation**:
```python
async def create_entity_relations(bubble, entity_name):
    """Create relations to other entities sharing same tags."""
    async with get_obsidian_client() as obsidian:
        # Find related entities
        for entity in bubble.entities:
            # Find other entities with same tag
            related = await obsidian.call_tool("search_nodes", {
                "query": {"entities": entity}
            })

            for related_entity in related:
                if related_entity["name"] != entity_name:
                    await obsidian.call_tool("create_relations", {
                        "from": entity_name,
                        "to": related_entity["name"],
                        "label": f"Shares {entity}"
                    })
```

---

### Story 8: Add Manual Sync Trigger Tool

**As a** Brain OS user
**I want** to manually trigger Obsidian → Neo4j sync
**So that** I don't have to wait 15 minutes for changes to sync

**Acceptance Criteria**:
- [ ] New tool: `sync_obsidian_now()`
- [ ] Immediately runs `sync_obsidian_to_neo4j()` function
- [ ] Returns summary of sync results
- [ ] Does not interfere with cron job (cron continues on schedule)

**Technical Implementation**:
```python
@mcp.tool
async def sync_obsidian_now() -> str:
    """Manually trigger Obsidian → Neo4j sync."""
    await sync_obsidian_to_neo4j()
    return "✅ Manual sync complete. Check logs for details."
```

---

## Technical Requirements

### Dependencies

**Python (Brain OS)**:
- `PyYAML` - Parse YAML frontmatter from Obsidian files
- `watchdog` (optional) - File system monitoring for instant sync

### File Changes

**New Files**:
- `src/utils/obsidian_parser.py` - Parse Obsidian entity files
- `src/utils/obsidian_sync.py` - Sync logic (detect changes, update Neo4j)
- `src/tools/memory/bulk_export.py` - Bulk export tool
- `logs/obsidian_sync_conflicts.log` - Conflict resolution log
- `/tmp/brainos_last_obsidian_sync.txt` - Last sync timestamp state

**Modified Files**:
- `brainos_server.py` - Add background sync task
- `src/database/queries/memory.py` - Add `update_bubble_from_obsidian()`
- `pyproject.toml` - Add `PyYAML` dependency

### Environment Variables

```env
# Obsidian Sync Configuration
OBSIDIAN_VAULT_PATH=/home/user/brain-os-vault
OBSIDIAN_SYNC_INTERVAL_MINUTES=15  # Cron job interval
```

---

## Testing Plan

### Unit Tests

1. **Test Obsidian Parser**:
   - Valid file with frontmatter + observations → parsed correctly
   - Missing frontmatter → raises ValueError
   - Missing observations section → returns empty list
   - UTF-8 encoding with special chars → handles correctly

2. **Test Change Detection**:
   - File modified after `since` → included in results
   - File modified before `since` → not included
   - Non-markdown files → ignored
   - .obsidian directory → ignored

3. **Test Conflict Resolution**:
   - Neo4j newer → returns "neo4j"
   - Obsidian newer → returns "obsidian"
   - Equal timestamps → returns "no_conflict"

### Integration Tests

1. **Test Bidirectional Sync**:
   - Create memory in Brain OS → appears in Obsidian
   - Edit file in Obsidian → updates Neo4j after cron
   - Edit both → newest wins

2. **Test Bulk Export**:
   - Export 20 memories → all appear in Obsidian
   - Export again → skips existing, no duplicates
   - Check graph view → all entities visible

3. **Test Manual Sync**:
   - Edit 3 files in Obsidian
   - Call `sync_obsidian_now()`
   - Verify Neo4j updated immediately

---

## Success Metrics

**Phase 2 Complete When**:
- ✅ Cron job syncs every 15 minutes automatically
- ✅ Edit Obsidian file → Neo4j updates within 15 minutes
- ✅ Bulk export 50+ memories successfully
- ✅ Obsidian graph view shows entity relationships
- ✅ Conflicts resolved correctly (newest wins)
- ✅ Manual sync works on-demand

**User Acceptance**:
- ✅ User edits observation in Obsidian
- ✅ User waits 15 minutes (or triggers manual sync)
- ✅ User queries Neo4j → sees updated observation
- ✅ User confirms "Bidirectional sync works"

---

## Out of Scope (Phase 3)

**NOT in Phase 2**:
- ❌ Voice memo processing (Phase 3)
- ❌ Daily notes automation (Phase 3)
- ❌ AI-powered relationship inference (Phase 3)
- ❌ Real-time sync (current: 15-minute cron)
- ❌ Web interface for managing sync (future enhancement)

---

## Estimated Effort

| Story | Complexity | Effort |
|-------|------------|--------|
| Story 1: Parse Obsidian Files | Medium | 3 hours |
| Story 2: Detect Changed Files | Low | 2 hours |
| Story 3: Update Neo4j from Obsidian | High | 4 hours |
| Story 4: Cron Job Background Task | Medium | 3 hours |
| Story 5: Conflict Resolution | Medium | 3 hours |
| Story 6: Bulk Export | Medium | 3 hours |
| Story 7: Entity Relations | Medium | 3 hours |
| Story 8: Manual Sync Tool | Low | 1 hour |

**Total Estimated Effort**: 22 hours

**Timeline**: 2-3 days of focused development

---

## Next Steps After Phase 2 Approval

1. User reviews Phase 2 user stories
2. User approves Phase 2 scope
3. I implement after Phase 1 completion
4. User tests bidirectional sync locally
5. User approves Phase 2 completion
6. Move to Phase 3: Voice memo + advanced workflows

---

**Phase 2 Status**: ⏳ Awaiting User Approval (after Phase 1)
**Dependencies**: Phase 1 must be completed first
**Next Action**: User reviews Phase 2 user stories
