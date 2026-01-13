# Phase 1: Basic Obsidian Integration
**Goal**: When I create a memory in Brain OS → File appears in Obsidian vault

---

## Overview

Phase 1 establishes the foundational connection between Brain OS and Obsidian. When you create a memory using Brain OS tools, a corresponding markdown file is instantly created in your local Obsidian vault.

**Success Criteria**:
- ✅ Brain OS connects to Obsidian MCP server
- ✅ `create_memory` tool creates file in Obsidian vault
- ✅ File contains all memory data (content, entities, observations, metadata)
- ✅ File is visible in Obsidian immediately after creation
- ✅ Works with local Obsidian (free version)

**Out of Scope**:
- ❌ Obsidian → Neo4j sync (Phase 2)
- ❌ Voice memo processing (Phase 3)
- ❌ Daily notes automation (Phase 3)

---

## User Stories

### Story 1: Setup Obsidian MCP Server Locally

**As a** developer
**I want to** install and run the Obsidian MCP server locally
**So that** Brain OS can communicate with my Obsidian vault

**Acceptance Criteria**:
- [ ] YuNaga224/obsidian-memory-mcp repository cloned
- [ ] Dependencies installed (`npm install`)
- [ ] Server built successfully (`npm run build`)
- [ ] Server runs on http://localhost:8001
- [ ] Test vault created at `/home/user/brain-os-vault`
- [ ] Server connects to test vault (MEMORY_DIR configured)
- [ ] Health check endpoint responds

**Technical Notes**:
```bash
# Commands to run
git clone https://github.com/YuNaga224/obsidian-memory-mcp.git
cd obsidian-memory-mcp
npm install
npm run build
MEMORY_DIR=/home/user/brain-os-vault node dist/index.js
```

**Verification**:
```bash
# Test server is running
curl http://localhost:8001/health
# Should return: {"status":"healthy"}
```

---

### Story 2: Add Obsidian MCP Client to Brain OS

**As a** Brain OS developer
**I want to** create an MCP client that connects to Obsidian server
**So that** Brain OS tools can call Obsidian MCP tools

**Acceptance Criteria**:
- [ ] New file created: `src/utils/obsidian_client.py`
- [ ] Function: `get_obsidian_client() -> AsyncClient`
- [ ] Reads `OBSIDIAN_MCP_URL` from environment (default: http://localhost:8001/mcp)
- [ ] Connection pooling configured
- [ ] Error handling for connection failures
- [ ] Unit test: Client connects successfully

**Technical Implementation**:
```python
# src/utils/obsidian_client.py
import os
from fastmcp import Client

async def get_obsidian_client():
    """Get Obsidian MCP client (singleton pattern)."""
    url = os.getenv("OBSIDIAN_MCP_URL", "http://localhost:8001/mcp")
    return Client(url)
```

**Verification**:
```python
# Test connection
async with get_obsidian_client() as client:
    tools = await client.list_tools()
    assert "create_entities" in tools
```

---

### Story 3: Create Entity Name Generator Utility

**As a** developer
**I want to** generate clean entity names from memory content
**So that** Obsidian files have readable, consistent names

**Acceptance Criteria**:
- [ ] New function: `generate_entity_name(content: str, entities: list[str]) -> str`
- [ ] Uses title case with underscores (e.g., "PostgreSQL_Decision")
- [ ] Limits to 50 characters max
- [ ] Removes special characters
- [ ] Handles edge cases (empty entities, long content)
- [ ] Unit tests for various inputs

**Examples**:
```python
generate_entity_name(
    content="Chose PostgreSQL over MongoDB for ACID compliance",
    entities=["PostgreSQL", "MongoDB", "Project X"]
)
# Returns: "PostgreSQL_vs_MongoDB_Decision"

generate_entity_name(
    content="Met with FastTrack client about N8N workflow",
    entities=["FastTrack", "N8N Workflow"]
)
# Returns: "FastTrack_N8N_Workflow_Meeting"
```

**Technical Notes**:
- Extract first 3-5 keywords from content
- Combine with first entity
- Fallback: Use first 30 chars of content if entities empty

---

### Story 4: Enhance `create_memory` to Sync to Obsidian

**As a** Brain OS user
**I want** `create_memory` to create both Neo4j bubble AND Obsidian file
**So that** my memories are visible in Obsidian immediately

**Acceptance Criteria**:
- [ ] `create_memory` tool calls Obsidian MCP after Neo4j insert
- [ ] Obsidian entity created with:
  - Name: Generated from content + entities
  - EntityType: Memory sector (Episodic, Semantic, etc.)
  - Observations: All observations from memory
  - Metadata: salience, memory_type, neo4j_id, created_at, source
- [ ] If Obsidian sync fails, Neo4j memory still created (fallback)
- [ ] Success message includes: "Memory stored in Neo4j (ID) and Obsidian (entity name)"
- [ ] Error message if Obsidian fails: "Memory stored in Neo4j, Obsidian sync failed: {error}"

**Technical Implementation**:
```python
# src/tools/memory/create_memory.py (enhanced)

@mcp.tool
async def create_memory(...) -> str:
    # Step 1: Create in Neo4j (existing logic)
    bubble_id = await upsert_bubble(...)

    # Step 2: Sync to Obsidian
    try:
        async with get_obsidian_client() as obsidian:
            entity_name = generate_entity_name(content, entities)

            await obsidian.call_tool("create_entities", {
                "name": entity_name,
                "entityType": sector,
                "observations": observations,
                "metadata": {
                    "salience": salience,
                    "memory_type": memory_type,
                    "neo4j_id": bubble_id,
                    "created": created_at.isoformat(),
                    "source": source
                }
            })

            return f"✅ Memory stored:\n- Neo4j ID: {bubble_id}\n- Obsidian: {entity_name}.md"

    except Exception as e:
        return f"✅ Memory stored in Neo4j: {bubble_id}\n⚠️ Obsidian sync failed: {e}"
```

**Verification**:
1. Run Brain OS server
2. Call `create_memory` with test data
3. Check Neo4j: Bubble exists
4. Check Obsidian vault: File exists at `entities/{name}.md`
5. Open file in Obsidian: See all metadata

---

### Story 5: Create Obsidian Entity File Structure

**As a** Brain OS user
**I want** Obsidian files to have structured, readable format
**So that** I can browse memories naturally in Obsidian

**Acceptance Criteria**:
- [ ] YuNaga224 server creates files in `entities/` directory
- [ ] File name format: `{Entity_Name}.md`
- [ ] YAML frontmatter includes:
  - `entityType: {sector}`
  - `created: {ISO timestamp}`
  - `updated: {ISO timestamp}`
  - `salience: {0.0-1.0}`
  - `memory_type: {instinctive|thinking|dormant}`
  - `source: {source}`
  - `neo4j_id: {bubble_id}`
- [ ] Markdown body includes:
  - Title: `# {Entity Name}`
  - `## Observations` section with bullet list
  - `## Metadata` section with details
- [ ] File is UTF-8 encoded
- [ ] Special characters handled correctly

**Example File**: `entities/PostgreSQL_Decision.md`
```markdown
---
entityType: Semantic
created: 2026-01-13T10:30:00Z
updated: 2026-01-13T10:30:00Z
salience: 0.85
memory_type: instinctive
source: direct_chat
neo4j_id: mem_abc123
---

# PostgreSQL Decision

## Observations
- Financial data requires ACID transactions
- Regulatory compliance critical
- Team familiar with SQL
- MongoDB ruled out: eventual consistency risk

## Metadata
- **Sector**: Semantic (Decision/Knowledge)
- **Salience**: 0.85 (business-critical)
- **Memory Type**: Instinctive (auto-activates)
- **Created**: 2026-01-13 10:30 UTC
- **Neo4j ID**: mem_abc123
```

**Verification**:
1. Create memory with long observations list
2. Open in Obsidian
3. Verify YAML frontmatter parses correctly
4. Verify markdown renders properly
5. Check UTF-8 encoding (test with emojis, special chars)

---

### Story 6: Add Environment Variable for Obsidian MCP URL

**As a** developer
**I want** configurable Obsidian MCP server URL
**So that** I can switch between local and remote Obsidian servers

**Acceptance Criteria**:
- [ ] New env var: `OBSIDIAN_MCP_URL` in `.env.example`
- [ ] Default value: `http://localhost:8001/mcp`
- [ ] CLAUDE.md updated with Obsidian configuration section
- [ ] README updated with setup instructions
- [ ] docker-compose.yml includes Obsidian MCP service (optional)

**Documentation Addition to CLAUDE.md**:
```markdown
## Obsidian Integration (Phase 4.1)

### Setup Obsidian MCP Server

1. Clone YuNaga224/obsidian-memory-mcp:
   ```bash
   git clone https://github.com/YuNaga224/obsidian-memory-mcp.git
   cd obsidian-memory-mcp
   npm install && npm run build
   ```

2. Create Brain OS vault:
   ```bash
   mkdir -p /home/user/brain-os-vault/entities
   ```

3. Run Obsidian MCP server:
   ```bash
   MEMORY_DIR=/home/user/brain-os-vault node dist/index.js
   ```

4. Configure Brain OS:
   ```env
   OBSIDIAN_MCP_URL=http://localhost:8001/mcp
   ```

5. Test connection:
   ```bash
   curl http://localhost:8001/health
   ```
```

---

### Story 7: Test End-to-End Memory Creation

**As a** Brain OS user
**I want** to create a memory and see it in Obsidian
**So that** I can verify the integration works

**Acceptance Criteria**:
- [ ] Brain OS server running (with Neo4j + Obsidian MCP)
- [ ] Obsidian desktop app open with brain-os-vault
- [ ] Create memory via Claude Desktop or MCP client:
  ```
  content: "Chose PostgreSQL for Project X due to ACID compliance"
  sector: "Semantic"
  entities: ["PostgreSQL", "Project X"]
  observations: ["Financial data needs transactions", "Team knows SQL"]
  salience: 0.85
  memory_type: "instinctive"
  ```
- [ ] Verify Neo4j: Bubble exists with correct data
- [ ] Verify Obsidian: File appears in entities/ folder
- [ ] Open file in Obsidian: All data visible
- [ ] Obsidian graph view: Entity node appears
- [ ] No errors in Brain OS logs
- [ ] No errors in Obsidian MCP logs

**Test Script** (Python):
```python
# test_phase1.py
import asyncio
from fastmcp import Client

async def test_create_memory():
    async with Client("http://localhost:9131/mcp") as brain:
        result = await brain.call_tool("create_memory", {
            "content": "Chose PostgreSQL for Project X due to ACID compliance",
            "sector": "Semantic",
            "entities": ["PostgreSQL", "Project X"],
            "observations": [
                "Financial data needs transactions",
                "Team knows SQL"
            ],
            "salience": 0.85,
            "memory_type": "instinctive",
            "source": "test_script"
        })
        print(result)
        assert "Neo4j" in result
        assert "Obsidian" in result

asyncio.run(test_create_memory())
```

**Manual Verification**:
1. Run test script
2. Check Neo4j Browser: Query `MATCH (b:Bubble) RETURN b LIMIT 1`
3. Open Obsidian vault
4. Find `entities/PostgreSQL_Project_X.md` (or similar name)
5. Open file, verify content
6. Open graph view, see new node

---

### Story 8: Handle Obsidian MCP Server Offline

**As a** Brain OS developer
**I want** graceful degradation when Obsidian MCP is offline
**So that** Brain OS continues working even if Obsidian sync fails

**Acceptance Criteria**:
- [ ] If Obsidian MCP unreachable, log warning
- [ ] Memory still created in Neo4j (don't fail entire operation)
- [ ] Return message: "✅ Memory stored in Neo4j, ⚠️ Obsidian unavailable"
- [ ] Connection timeout: 5 seconds
- [ ] Retry logic: 1 retry with 2-second delay
- [ ] Health check: Periodic ping to Obsidian MCP (every 60s)

**Technical Implementation**:
```python
async def sync_to_obsidian(bubble_id, entity_data):
    """Sync to Obsidian with error handling."""
    try:
        async with asyncio.timeout(5):  # 5-second timeout
            async with get_obsidian_client() as obsidian:
                await obsidian.call_tool("create_entities", entity_data)
                return True
    except asyncio.TimeoutError:
        logger.warning(f"Obsidian sync timeout for {bubble_id}")
        return False
    except Exception as e:
        logger.error(f"Obsidian sync failed for {bubble_id}: {e}")
        return False
```

**Verification**:
1. Stop Obsidian MCP server
2. Create memory via Brain OS
3. Verify: Neo4j memory created
4. Verify: Warning logged
5. Verify: User message mentions Obsidian unavailable
6. Start Obsidian MCP server
7. Create another memory
8. Verify: Both Neo4j and Obsidian updated

---

## Technical Requirements

### Dependencies

**Python (Brain OS)**:
- `fastmcp>=2.14.2` (already installed)
- No new dependencies required

**Node.js (Obsidian MCP)**:
- Node.js v18+
- YuNaga224/obsidian-memory-mcp

### File Changes

**New Files**:
- `src/utils/obsidian_client.py` - Obsidian MCP client utility
- `src/utils/entity_naming.py` - Entity name generation
- `test_phase1.py` - Integration test script
- `docs/project/phase4/phase1_user_stories.md` - This document

**Modified Files**:
- `src/tools/memory/create_memory.py` - Add Obsidian sync
- `CLAUDE.md` - Add Obsidian setup instructions
- `.env.example` - Add `OBSIDIAN_MCP_URL`

### Environment Variables

```env
# Obsidian Integration
OBSIDIAN_MCP_URL=http://localhost:8001/mcp  # URL to Obsidian MCP server
```

---

## Testing Plan

### Unit Tests

1. **Test Entity Name Generation**:
   - Empty entities → fallback to content
   - Long content → truncate to 50 chars
   - Special characters → sanitize
   - Multiple entities → combine first 2-3

2. **Test Obsidian Client**:
   - Connection successful → returns client
   - Connection fails → logs error, returns None
   - Timeout → raises asyncio.TimeoutError

3. **Test create_memory Enhancement**:
   - Neo4j insert successful → bubble created
   - Obsidian sync successful → entity created
   - Obsidian sync fails → Neo4j still succeeds

### Integration Tests

1. **End-to-End Memory Creation**:
   - Create memory with full data
   - Verify Neo4j bubble exists
   - Verify Obsidian file exists
   - Verify file content matches input

2. **Error Handling**:
   - Obsidian MCP offline → Neo4j succeeds, warning logged
   - Neo4j offline → entire operation fails
   - Invalid data → validation error before any DB writes

3. **Obsidian File Format**:
   - YAML frontmatter parses correctly
   - Markdown renders in Obsidian
   - Graph view shows entity
   - Search finds entity by content

---

## Success Metrics

**Phase 1 Complete When**:
- ✅ 10+ test memories created successfully
- ✅ All memories visible in Neo4j Browser
- ✅ All memories have corresponding Obsidian files
- ✅ Obsidian graph view displays all entities
- ✅ Search in Obsidian finds entities by content
- ✅ No errors in logs for normal operation
- ✅ Graceful degradation when Obsidian offline

**User Acceptance**:
- ✅ User can create memory via Brain OS
- ✅ User sees file appear in Obsidian instantly
- ✅ User can open file in Obsidian, read content
- ✅ User can search in Obsidian, find memory
- ✅ User confirms "This works as expected"

---

## Out of Scope (Future Phases)

**NOT in Phase 1**:
- ❌ Obsidian → Neo4j sync (Phase 2)
- ❌ Cron job for bidirectional sync (Phase 2)
- ❌ Voice memo processing (Phase 3)
- ❌ Daily notes automation (Phase 3)
- ❌ Relationship creation between entities (Phase 2/3)
- ❌ Bulk export of existing memories (Phase 2)
- ❌ Docker compose integration (Phase 2)
- ❌ Production deployment (Phase 3)

---

## Estimated Effort

| Story | Complexity | Effort |
|-------|------------|--------|
| Story 1: Setup Obsidian MCP | Low | 1 hour |
| Story 2: Add MCP Client | Low | 1 hour |
| Story 3: Entity Name Generator | Medium | 2 hours |
| Story 4: Enhance create_memory | Medium | 3 hours |
| Story 5: File Structure | Low | 1 hour |
| Story 6: Environment Config | Low | 1 hour |
| Story 7: End-to-End Test | Medium | 2 hours |
| Story 8: Error Handling | Medium | 2 hours |

**Total Estimated Effort**: 13 hours

**Timeline**: 1-2 days of focused development

---

## Next Steps After Phase 1 Approval

1. User reviews this document
2. User approves Phase 1 scope
3. I proceed with implementation:
   - Story 1-3: Setup and utilities
   - Story 4-5: Core integration
   - Story 6-8: Testing and polish
4. User tests locally with Obsidian
5. User approves Phase 1 completion
6. Move to Phase 2: Bidirectional sync

---

**Phase 1 Status**: ⏳ Awaiting User Approval
**Next Action**: User reviews user stories, approves to proceed
