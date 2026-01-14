# Query Memories Tool - Implementation Plan

**Date**: 2026-01-14
**Status**: Ready for Implementation
**Type**: New Feature (SimpleMem-inspired)

---

## Executive Summary

The `query_memories` tool provides AI-generated answers with reasoning and confidence scores, filling a critical gap in BrainOS's current retrieval capabilities. Unlike existing tools that return raw memory data, this tool synthesizes a direct natural language answer with full reasoning trace.

**Key Difference from SimpleMem**:
- SimpleMem: Returns `{answer, reasoning, confidence, num_memories_used}`
- BrainOS `get_memory_relations`: Returns structured data (themes, insights, relationships) but NO synthesized answer

This tool bridges the gap by providing the missing `answer`, `reasoning`, and `confidence` components.

---

## Obsidian Integration Analysis

### Current State (Phase 5.1)

**Data Flow: Neo4j → Obsidian (one-way)**

```
┌─────────────────┐              ┌─────────────────┐
│  Claude / User  │────create────▶│     Neo4j       │────sync────▶
│                 │    _memory()  │  (Source of     │   (mirror)   │
└─────────────────┘              │   Truth)        │              │
                                 └─────────────────┘              │
                                                                  │
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │  Obsidian Vault │
                                                         │  (Write-only)   │
                                                         │  .md files      │
                                                         └─────────────────┘
```

**Key Characteristics:**
- Neo4j is the **source of truth**
- Obsidian is a **read-only mirror** (writes only via Neo4j sync)
- Every `create_memory()` triggers immediate Obsidian sync
- Obsidian files contain duplicate Neo4j data with YAML frontmatter

**Implication for `query_memories`:**
- Query **Neo4j only** - Obsidian is just a mirror copy
- No need to parse Obsidian markdown files
- Data is identical in both systems (eventually consistent)

---

### Future State (Phase 5.2 - Bidirectional Sync)

**Data Flow: Neo4j ⇄ Obsidian (two-way)**

```
┌─────────────────┐              ┌─────────────────┐
│  Obsidian Vault │────sync──────▶│     Neo4j       │
│  (Editable)     │   (cron 15m)  │  (Source of     │
│                 │   + manual    │   Truth)        │
│  - User edits   │              │                 │
│  - New notes    │◀─────sync────┤                 │
└─────────────────┘              └─────────────────┘
        │                                  │
        │                                  │
        ▼                                  ▼
  User can edit                      Query from here
  in Obsidian app
```

**Key Characteristics:**
- Users can edit memories directly in Obsidian
- Background cron job syncs Obsidian → Neo4j every 15 minutes
- Manual sync available via `sync_obsidian_now()` tool
- Conflict resolution: newest timestamp wins

**Implication for `query_memories`:**
- **Primary data source: Neo4j** (still the source of truth)
- **Sync window**: Up to 15 minutes of staleness if user edits in Obsidian
- **User action**: Can trigger `sync_obsidian_now()` before querying for freshest data
- **Design decision**: Keep Neo4j as single source (simpler architecture)

---

### Design Decision: Neo4j as Single Source

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Primary data source** | Neo4j only | Source of truth, faster queries |
| **Obsidian fallback** | Not needed (Phase 5.1) | Obsidian is mirror copy |
| **Obsidian fallback** | Optional (Phase 5.2) | Only if no Neo4j results |
| **Sync before query** | User-initiated | Call `sync_obsidian_now()` manually |
| **Staleness notice** | Include in response | Warn if data might be stale |

**Why Not Query Obsidian Directly?**

1. **Performance**: Neo4j is optimized for queries (Cypher, indexing)
2. **Consistency**: Single source prevents divergence issues
3. **Complexity**: Parsing markdown files adds overhead
4. **Relationships**: Neo4j has `LINKED` relationships, Obsidian doesn't
5. **Salience**: Neo4j has dynamic salience scoring, Obsidian is static

---

### Summary: Obsidian Impact

| Phase | Obsidian Role | `query_memories` Behavior |
|-------|---------------|--------------------------|
| **5.1 (current)** | Write-only mirror | Query Neo4j only |
| **5.2 (future)** | Editable + bidirectional sync | Query Neo4j, optional sync first |

**Recommendation**: Implement `query_memories` with **Neo4j-only queries** for both phases. The sync window (15 min) is acceptable for most use cases, and power users can trigger manual sync when needed.

---

## Feature Comparison

| Feature | SimpleMem | BrainOS `get_memory_relations` | BrainOS `query_memories` (NEW) |
|---------|-----------|-------------------------------|-------------------------------|
| AI-generated answer | ✅ | ❌ | ✅ |
| Reasoning trace | ✅ | ❌ (only themes) | ✅ |
| Confidence score | ✅ | ❌ | ✅ |
| Hybrid retrieval | ✅ | ⚠️ (semantic only) | ✅ |
| Query complexity analysis | ✅ | ⚠️ (basic) | ✅ |
| Reflection for complex queries | ✅ | ❌ | ✅ |
| Number of memories used | ✅ | ✅ | ✅ |

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Question  │────▶│  Query Analysis │────▶│  Neo4j Hybrid   │
│  "When did I    │     │  (Groq ~100ms)  │     │  Retrieval      │
│   meet Alice?"  │     │                 │     │  (Keyword +     │
└─────────────────┘     └────────┬────────┘     │   Semantic)     │
                                 │               └────────┬────────┘
                                 │                        │
                                 │ 1. Extract concepts    │ 2. Retrieve memories
                                 │ 2. Classify complexity │
                                 │ 3. Determine strategy │
                                 ▼                        ▼
                         ┌─────────────────┐     ┌─────────────────┐
                         │  Answer         │◀────│  Retrieved      │
                         │  Synthesis      │     │  Context        │
                         │  (OpenRouter    │     │  (Memories +    │
                         │   ~2-5s)        │     │   Relations)    │
                         └────────┬────────┘     └─────────────────┘
                                  │
                                  │ 3. Generate answer
                                  │ 4. Build reasoning
                                  │ 5. Calculate confidence
                                  ▼
                         ┌─────────────────┐
                         │  Response       │
                         │  {answer,       │
                         │   reasoning,    │
                         │   confidence,   │
                         │   num_used}     │
                         └─────────────────┘
```

---

## Implementation Steps

### Step 1: Create Query Analysis Node (1-2 hours)
**File**: `src/flows/query_memories.py` (new file)

### Step 2: Create Hybrid Retrieval Node (2-3 hours)
**File**: `src/flows/query_memories.py` (add to existing file)

### Step 3: Create Answer Synthesis Node (2-3 hours)
**File**: `src/flows/query_memories.py` (add to existing file)

### Step 4: Wire the Flow (30 minutes)
**File**: `src/flows/query_memories.py` (add to end of file)

### Step 5: Create MCP Tool Wrapper (1 hour)
**File**: `src/tools/memory/query_memories.py` (new file)

### Step 6: Register Tool (15 minutes)
**File**: `src/tools/__init__.py`

### Step 7: Update Server Instructions (30 minutes)
**File**: `brainos_server.py`

### Step 8: Testing (2-3 hours)
**Files**: `tests/unit/test_query_memories.py`, `tests/integration/test_query_memories_tool.py`

---

## Files Summary

| File | Action | Lines | Purpose |
|------|--------|-------|---------|
| `src/flows/query_memories.py` | New | ~450 | Main flow with 4 nodes |
| `src/tools/memory/query_memories.py` | New | ~150 | MCP tool wrapper |
| `src/tools/__init__.py` | Modify | +3 | Register tool |
| `brainos_server.py` | Modify | +20 | Update instructions |
| `tests/unit/test_query_memories.py` | New | ~100 | Unit tests |
| `tests/integration/test_query_memories_tool.py` | New | ~50 | Integration test |

**Total**: ~773 lines added across 6 files

---

## Success Criteria

The `query_memories` tool is complete when:

- ✅ `query_memories_tool` available in MCP server
- ✅ Simple query returns direct answer with confidence >0.8
- ✅ Complex query triggers reflection and synthesis
- ✅ Reasoning includes memory references [1], [2], etc.
- ✅ Confidence score properly reflects uncertainty
- ✅ No memories found returns helpful message with suggestions
- ✅ All unit tests passing
- ✅ Integration test passes end-to-end

---

## Example Usage

### Simple Query
```
User: "When did I meet with Alice?"

Response:
## Answer
You met with Alice on January 10, 2026, to discuss the N8N workflow
integration for the FastTrack project.

## Reasoning
Found memory [1] which records the meeting on 2026-01-10 about N8N workflow
with Alice from FastTrack. The meeting was documented as an Episodic memory
with high salience (0.85), indicating it was important.

## Confidence
0.92 / 1.0 (Very Confident)

## Sources
1 memory entries used
```

### Complex Query
```
User: "Why did I choose PostgreSQL over MongoDB?"

Response:
## Answer
You chose PostgreSQL over MongoDB primarily for ACID compliance and transactional
integrity, which were critical for the financial data processing requirements
of the FastTrack project.

## Reasoning
Analyzed 3 memories:
- Memory [1] (Semantic, salience 0.90): Documents the decision stating "ACID
  compliance was non-negotiable for financial transactions"
- Memory [2] (Semantic, salience 0.75): Notes that MongoDB was considered but
  rejected due to "lack of native transaction support at the time"
- Memory [3] (Reflective, salience 0.70): Post-decision reflection confirming
  the choice was correct: "PostgreSQL has scaled well"

The decision was driven by technical requirements (ACID compliance) rather
than cost or familiarity.

## Confidence
0.88 / 1.0 (Confident)

## Sources
3 memory entries used
```

---

**Status**: Ready for implementation upon user approval
**Estimated Time**: 8-12 hours (1-1.5 days)
**Complexity**: Medium (4 PocketFlow nodes, LLM orchestration, confidence calculation)
