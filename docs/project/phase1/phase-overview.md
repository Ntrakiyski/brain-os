# Phase 1: Overview & Decisions

> **Purpose:** This document serves as onboarding material for new team members and context for Phase 2 development. It explains the architectural decisions made during Phase 1 and the reasoning behind them.

---

## Executive Summary

Phase 1 established the technical foundation for Brain OS by implementing:
1. **FastMCP server** with three tools (create_memory, get_memory, list_sectors)
2. **Neo4j integration** with async connection pooling and Cypher queries
3. **Claude Desktop integration** using FastMCP CLI installer
4. **Configuration management** using frozen dataclasses
5. **Dual-LLM setup** preparing for System 1 (fast) and System 2 (deep) thinking

The phase concluded with a fully functional persistent memory system accessible from Claude Desktop.

---

## Architecture Decisions

### 1. Why FastMCP over Official MCP SDK?

**Decision:** Use FastMCP 2.x as the MCP server framework.

**Alternatives Considered:**
- Official MCP Python SDK (`modelcontextprotocol`)
- Direct implementation of MCP protocol

**Rationale:**
| Factor | FastMCP | Official SDK |
|--------|---------|--------------|
| **Abstraction level** | High-level decorators | Low-level protocol |
| **Boilerplate** | Minimal (@mcp.tool) | Extensive |
| **Claude Desktop integration** | Built-in CLI installer | Manual config |
| **Dependency management** | `uv` integration | Manual pip |
| **Documentation** | gofastmcp.com | modelcontextprotocol.io |
| **Maintenance** | Active (Prefect-backed) | Community |

**Trade-offs:**
- **Pro:** 10x less code for same functionality
- **Pro:** `fastmcp install claude-desktop` handles path resolution automatically
- **Con:** Additional dependency (but maintained by Prefect team)

**Outcome:** FastMCP reduced server implementation to ~100 lines vs ~500 lines with official SDK.

---

### 2. Why Neo4j over PostgreSQL/MongoDB?

**Decision:** Use Neo4j Community Edition as the primary database.

**Alternatives Considered:**
- PostgreSQL with `ltree` or adjacency lists
- MongoDB with document references
- Redis graph (limited query capabilities)

**Rationale:**

**1. Native Graph Operations**
```cypher
-- Neo4j: Direct relationship traversal
MATCH (a:Bubble)-[:RELATES_TO]->(b:Bubble)
WHERE a.sector = 'Episodic'
RETURN b

-- PostgreSQL: Recursive CTE required
WITH RECURSIVE rels AS (
  SELECT id, related_id FROM bubbles WHERE id = ?
  UNION ALL
  SELECT b.id, b.related_id FROM bubbles b
  JOIN rels r ON b.id = r.related_id
)
SELECT * FROM rels
```

**2. Visual Debugging**
- Neo4j Browser at `http://localhost:7474` provides real-time graph visualization
- Essential for understanding neurochain connections in Phase 2

**3. Performance Characteristics**
| Operation | Neo4j | PostgreSQL (Adjacency List) |
|-----------|-------|------------------------------|
| Single-hop query | O(1) | O(1) |
| Multi-hop traversal | O(depth) | O(breadth^depth) |
| Path finding | Optimized | Requires CTEs |

**4. Future-Proofing for Phase 2**
- Salience scoring requires relationship weights
- Neurochain architecture needs single-waypoint connections
- Synaptic weight queries are native graph operations

**Trade-offs:**
- **Pro:** Designed for graphs, not hacked on
- **Pro:** Cypher query language is declarative and expressive
- **Con:** Slower than PostgreSQL for simple table scans
- **Con:** Requires learning Cypher (but ~80% SQL knowledge transfers)

**Outcome:** Neo4j's graph-first design aligns with Brain OS's memory-as-neuro-network metaphor.

---

### 3. Why Async/Await over Synchronous Code?

**Decision:** Use `async/await` throughout the codebase.

**Alternatives Considered:**
- Synchronous Neo4j driver
- Thread-based concurrency

**Rationale:**

**1. I/O-Bound Workload**
```
Timeline: [LLM Call ----->] [DB Query ----->] [DB Query ----->]
Async:    [LLM Call ----->] [DB Query ----->] [DB Query ----->]
Threads:  [Thread 1: LLM]   [Thread 2: DB]    [Thread 3: DB]
```

- MCP server waits for LLM responses (Network I/O)
- Neo4j queries are database I/O
- Async allows handling multiple requests without thread overhead

**2. Neo4j Driver Support**
- Official `neo4j` async driver is first-party supported
- Same API as sync driver but returns coroutines
- Connection pooling handled internally

**3. Future Scalability**
- Phase 2 will introduce concurrent LLM calls (Groq + OpenRouter)
- Phase 3 may add real-time features
- Async foundation prevents rewrites

**Trade-offs:**
- **Pro:** Efficient resource utilization (single-threaded concurrency)
- **Pro:** No GIL contention for I/O operations
- **Con:** Slightly more complex code (async/await keywords)
- **Con:** Some libraries don't support async (workaround: run in executor)

**Outcome:** Async provides headroom for multi-agent workflows in Phase 2.

---

### 4. Why Docker Compose for Neo4j?

**Decision:** Run Neo4j via Docker Compose with persistent volumes.

**Alternatives Considered:**
- Native installation (brew/apt/chocolate)
- Neo4j Desktop (GUI application)
- Cloud-hosted Neo4j Aura (free tier limited)

**Rationale:**

**1. Environment Parity**
```bash
# Same commands work everywhere
docker-compose up -d    # Local dev
docker-compose -f docker-compose.prod.yml up -d  # Production
```

**2. Dependency Isolation**
- No Neo4j installation on host machine
- No version conflicts with other projects
- Clean teardown: `docker-compose down -v`

**3. Configuration as Code**
```yaml
# docker-compose.yml is version-controlled
services:
  neo4j:
    image: neo4j:5.25-community  # Pinned version
    environment:
      - NEO4J_AUTH=neo4j/brainos_password_123
    volumes:
      - neo4j_data:/data  # Persistent storage
```

**4. Team Onboarding**
- New developers run two commands: `git clone` + `docker-compose up -d`
- No manual Neo4j installation guide needed

**Trade-offs:**
- **Pro:** Reproducible across machines (Mac/Linux/Windows)
- **Pro:** Easy version upgrades (change image tag)
- **Pro:** Data persistence across container restarts
- **Con:** Requires Docker installed (~500MB download)
- **Con:** Slight performance overhead (~5% vs native)

**Outcome:** Docker's developer experience benefits outweigh minimal performance cost.

---

### 5. Why Pydantic for Validation?

**Decision:** Use Pydantic v2 for all data validation.

**Alternatives Considered:**
- Manual validation with `if` statements
- Marshmallow (older serialization library)
- Type hints only (mypy/static analysis only)

**Rationale:**

**1. Automatic Documentation Generation**
```python
@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    salience: float = Field(default=0.5, ge=0.0, le=1.0),
) -> str:
    ...
```
- FastMCP extracts `Field()` descriptions
- LLM receives structured parameter documentation
- No separate API doc maintenance

**2. Runtime Type Safety**
```python
# Fails fast with clear error
BubbleCreate(content="", sector="Invalid", salience=2.0)
# ValidationError: 3 errors
# - content: String should have at least 1 character
# - sector: sector must be one of: Episodic, Semantic, ...
# - salience: Input should be less than or equal to 1.0
```

**3. IDE Support**
- Autocomplete works with Pydantic models
- Type checkers understand validated types
- Refactoring is safer

**Trade-offs:**
- **Pro:** Declarative validation rules
- **Pro:** Clear error messages for users
- **Pro:** Minimal boilerplate
- **Con:** Slight learning curve for validators
- **Con:** Runtime overhead (~1ms per validation)

**Outcome:** Pydantic's validation clarity improves debugging and LLM understanding.

---

### 6. Why Root-Level Server File?

**Decision:** Create `brainos_server.py` at project root instead of using `src/main.py`.

**Problem Encountered:**
```json
// Claude Desktop config with relative path
{
  "args": ["run", "fastmcp", "run", "src/tools/memory_tools.py:mcp"],
  "cwd": "C:\\Users\\nikol\\Desktop\\new-apps\\0brainOS"
}
```

**Error:** `File not found: C:\Users\nikol\AppData\Local\AnthropicClaude\app-1.0.2339\src\tools\memory_tools.py`

**Root Cause:**
- `uv run` processes arguments before changing to `cwd`
- Relative paths resolve from Claude Desktop's install directory, not `cwd`
- FastMCP CLI installer handles this, but manual config doesn't

**Solution:**
```python
# brainos_server.py (at project root)
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP

mcp = FastMCP("Brain OS")

# Tools defined here...
```

```json
// Claude Desktop config with absolute path
{
  "args": ["run", "C:\\Users\\nikol\\Desktop\\new-apps\\0brainOS\\brainos_server.py:mcp"]
}
```

**Rationale:**
- **Recommended approach:** `fastmcp install claude-desktop` handles paths automatically
- **Fallback:** Root-level file with absolute paths works manually
- **Documentation:** Shows both methods for different use cases

**Outcome:** Documented path resolution gotcha for future reference.

---

### 7. Why Frozen Dataclasses for Configuration?

**Decision:** Use `@dataclass(frozen=True)` for all configuration objects.

**Alternatives Considered:**
- Regular dictionaries
- `pydantic.BaseModel`
- Mutable dataclasses

**Rationale:**

**1. Immutability Prevents Drift**
```python
# Bad: Mutable config allows accidental changes
config = Neo4jConfig(uri="bolt://localhost:7687", user="neo4j", password="secret")
config.uri = "bolt://attacker.example:7687"  # Oops!

# Good: Frozen config raises error
config = Neo4jConfig(uri="bolt://localhost:7687", user="neo4j", password="secret")
config.uri = "bolt://attacker.example:7687"  # FrozenInstanceError!
```

**2. Hashable for Caching**
```python
# Phase 2 can use configs as cache keys
@lru_cache
def get_llm_client(config: GroqConfig) -> Groq:
    return Groq(api_key=config.api_key)
```

**3. Clear Intent**
```python
# Dataclass: "This is a data holder"
@dataclass(frozen=True)
class Neo4jConfig:
    uri: str
    user: str
    password: str

# BaseModel: "This requires validation"
class Neo4jConfig(BaseModel):
    uri: str
    user: str
    password: str
```

**Trade-offs:**
- **Pro:** No accidental mutations
- **Pro:** Lightweight (no Pydantic overhead for simple config)
- **Pro:** Type hints work with IDEs
- **Con:** No runtime validation (but env vars are typed)
- **Con:** Can't use default factories easily

**Outcome:** Frozen dataclasses balance simplicity and safety.

---

### 8. Why Global Connection Singleton?

**Decision:** Use module-level singleton `_connection` for Neo4j driver.

**Alternatives Considered:**
- Dependency injection (pass connection to every function)
- Context managers (create/destroy per request)
- Connection pooling library

**Rationale:**

**1. Driver Manages Its Own Pool**
```python
# Neo4j driver internally maintains connection pool
driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
# ~10 connections kept alive automatically
```

**2. Lazy Initialization**
```python
async def get_connection():
    global _connection
    if _connection is None:
        _connection = Neo4jConnection(...)
        await _connection.connect()
    return _connection
```
- Connection established on first use
- Not at import time (faster startup)
- Not on every request (would be slow)

**3. MCP Server Lifecycle**
- FastMCP server runs as single process
- No forking/threading that would require separate connections
- Shutdown can call `close_connection()` explicitly

**Trade-offs:**
- **Pro:** Efficient resource usage
- **Pro:** Simple call sites (just `await get_connection()`)
- **Pro:** Driver handles pool automatically
- **Con:** Global state (but acceptable for singleton app)
- **Con:** Harder to test (need to mock global)

**Outcome:** Singleton matches MCP server's single-process model.

---

### 9. Why Dual-LLM Configuration?

**Decision:** Configure both Groq (fast) and OpenRouter (deep) from Phase 1.

**Alternatives Considered:**
- Single LLM for all tasks
- Decide in Phase 2 when needed

**Rationale:**

**1. System 1 vs System 2 Thinking**
| Task Type | Best LLM | Reason |
|-----------|----------|--------|
| Sector classification | Groq (~100ms) | Simple categorization |
| Entity extraction | Groq (~200ms) | Structured output |
| Research synthesis | OpenRouter (~5s) | Complex reasoning |
| Creative writing | OpenRouter (~10s) | Nuance required |

**2. Cost Optimization**
- Groq: ~$0.10 per 1M tokens (hosted models)
- OpenRouter: ~$1-5 per 1M tokens (Claude/GPT-4)
- Use fast/cheap model when quality difference is negligible

**3. Configuration Readiness**
```python
# Config ready in Phase 1
groq = GroqConfig.from_env()  # For Phase 2 classification
openrouter = OpenRouterConfig.from_env()  # For Phase 2 synthesis
```

**Outcome:** Dual-LLM setup enables Phase 2 workflow design without refactoring.

---

## What Was NOT Implemented (Deferred to Phase 2)

| Feature | Why Deferred |
|---------|--------------|
| **PocketFlow workflows** | Phase 1 focused on foundational MCP tools |
| **Salience decay** | Requires background tasks (PocketFlow) |
| **Neurochain connections** | Phase 1 established Bubble nodes first |
| **Cloud synthesis** | Requires relationship structure |
| **LLM integration** | Database layer needed before AI layer |
| **Authentication** | Single-user local deployment doesn't need it |

---

## Key Learnings from Phase 1

### 1. Claude Desktop Path Resolution
**Lesson:** Relative paths in Claude Desktop config resolve from Claude's install directory, not the `cwd` directory.

**Fix:** Use FastMCP CLI installer or absolute paths.

### 2. Neo4j element_id Format
**Lesson:** Neo4j's `element_id` returns a string like `'4:uuid:0'`, not an integer.

**Fix:** Changed `BubbleResponse.id` from `int` to `str`.

### 3. Cypher Parameter Naming
**Lesson:** Don't use `query` as a Cypher parameter name when calling `session.run(cypher, query=...)`.

**Fix:** Renamed to `$search_query` to avoid conflict with positional `query` parameter.

---

## Files Created in Phase 1

```
0brainos/
├── src/
│   ├── core/config.py              # Configuration dataclasses
│   ├── database/
│   │   ├── connection.py           # Async connection singleton
│   │   └── queries.py              # Cypher query functions
│   ├── tools/memory_tools.py       # MCP tool definitions
│   └── utils/schemas.py            # Pydantic validation models
├── brainos_server.py               # Claude Desktop entry point
├── docker-compose.yml              # Neo4j container config
├── pyproject.toml                  # uv dependency specification
├── CLAUDE.md                       # Claude Code project guidance
└── docs/project/phase1/
    ├── user-stories.md             # This file
    ├── code-snippets.md            # Reference implementations
    └── phase-overview.md           # Decisions and rationale
```

---

## Starting Phase 2: What You Need to Know

### Prerequisites
1. **Read this document** - Understand architectural decisions
2. **Read code-snippets.md** - Learn key implementation patterns
3. **Run the server** - `docker-compose up -d && fastmcp run brainos_server.py:mcp`
4. **Test with Claude Desktop** - Verify MCP tools work end-to-end

### Phase 2 Foundation
The following are already in place:
- ✅ MCP server with tool framework
- ✅ Neo4j async connection with pooling
- ✅ Pydantic validation schemas
- ✅ Configuration management
- ✅ Claude Desktop integration

### Phase 2 Goals
1. **PocketFlow workflows** - Multi-agent orchestration
2. **Salience scoring** - Time-based importance decay
3. **Neurochain connections** - Relationships between bubbles
4. **Dual-LLM usage** - Groq for fast tasks, OpenRouter for deep thinking
5. **Cloud generation** - AI-synthesized insights

### Entry Points for Phase 2 Development
| File | Purpose |
|------|---------|
| `src/database/queries.py` | Add relationship queries (create synapse, get connected bubbles) |
| `src/tools/` | Add new tools (create_connection, decay_salience, synthesize_cloud) |
| `brainos_server.py` | Register new tools with `@mcp.tool` |
| `src/core/config.py` | Configuration already supports Groq/OpenRouter |

---

## Quick Reference: Phase 1 Commands

```bash
# Start Neo4j
docker-compose up -d

# Run MCP server (STDIO)
fastmcp run brainos_server.py:mcp

# Run with HTTP transport (for testing)
fastmcp run brainos_server.py:mcp --transport http --port 8000

# Install in Claude Desktop
fastmcp install claude-desktop brainos_server.py --project . --env-file .env

# Check Neo4j Browser
open http://localhost:7474  # neo4j / brainos_password_123
```

---

## Questions to Answer Before Phase 2

1. **Salience decay rate:** Should memories decay by 10% per day? Per week?
2. **Synaptic weights:** How do we calculate relationship strength? (Access frequency? Semantic similarity?)
3. **Cloud generation thresholds:** When should we synthesize a cloud? (N related memories? Time interval?)
4. **PocketFlow structure:** What are the agent workflows? (Ingestion → Classification → Storage → Synthesis)

These questions should be answered in Phase 2 planning based on Phase 1's stable foundation.
