# Phase 1: Technical Foundation

> **Status:** ✅ COMPLETED
>
> Phase 1 successfully established the foundational infrastructure for Brain OS, including MCP server integration, Neo4j persistence, Claude Desktop integration, and dual-LLM configuration.

## 1. Project Objective
Build a functional MCP server that provides a persistent connection between Claude and a Neo4j graph database. This phase implements the core "Read/Write" operations required for long-term memory.

## 2. Technical User Stories

### Stream A: MCP Interface (The API Layer)
**User Story:**
> As a user, I want to provide information to Claude and have it stored in a structured graph database, so that the context is preserved across different chat sessions.

**Acceptance Criteria:**
*   ✅ A FastMCP server is running and accessible to Claude.
*   ✅ The tool `create_memory` is exposed and functional.
*   ✅ The tool `get_memory` is exposed and functional.
*   ✅ The tool `list_sectors` is exposed and functional.
*   ✅ Claude can successfully call these tools and receive structured responses.

### Stream B: Neo4j Integration (The Persistence Layer)
**User Story:**
> As a system, I want to store data as nodes with specific metadata (timestamp, sector, source), so that I can perform structured queries and relational analysis later.

**Acceptance Criteria:**
*   ✅ The Python application maintains an asynchronous connection to a local Neo4j instance.
*   ✅ Data is stored using a consistent schema (Node Label: `Bubble`).
*   ✅ The system can perform keyword-based searches across stored nodes.
*   ✅ Database credentials are managed securely via environment variables.
*   ✅ Neo4j element_id handling (string format) properly configured.

### Stream C: Docker & Neo4j Setup (The Infrastructure Layer)
**User Story:**
> As a developer, I want to run Neo4j as a separate service, so that I have clean separation between application and database infrastructure.

**Acceptance Criteria:**
*   ✅ Neo4j can be deployed separately from BrainOS application
*   ✅ BrainOS connects to Neo4j via configurable `NEO4J_URI` environment variable
*   ✅ Neo4j data persists across container restarts using Docker volumes
*   ✅ Neo4j Browser is accessible at `http://localhost:7474` for manual queries (local dev)
*   ✅ The Bolt protocol is available for application connections
*   ✅ Production deployment separates Neo4j service from BrainOS to avoid env var conflicts

**Update Note:** Originally implemented with Neo4j in same docker-compose as BrainOS. Revised to external deployment after encountering Coolify environment variable sharing issues.

### Stream D: Claude Desktop Integration (The User Interface Layer) ✨ NEW
**User Story:**
> As a user, I want to use Brain OS directly from Claude Desktop, so that I don't need to run separate servers or manage HTTP connections.

**Acceptance Criteria:**
*   ✅ FastMCP CLI installer command documented for easy setup.
*   ✅ Server entry point (`brainos_server.py`) configured with proper path handling.
*   ✅ Claude Desktop config documented with absolute paths and environment variables.
*   ✅ Common integration issues documented (path resolution, environment variables).

### Stream E: Configuration Management (The Settings Layer) ✨ NEW
**User Story:**
> As a developer, I want centralized configuration management with type safety, so that settings are consistent and validated at startup.

**Acceptance Criteria:**
*   ✅ `src/core/config.py` provides frozen dataclass configurations.
*   ✅ Neo4j, Groq, and OpenRouter configs with `from_env()` class methods.
*   ✅ Five-sector ontology constants defined globally.
*   ✅ Proper error handling for missing API keys.

---

## 3. Actual Project Structure (As Implemented)

```text
0brainos/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Environment variables & global settings (frozen dataclasses)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py      # Neo4j async driver with global connection singleton
│   │   └── queries.py         # Granular Cypher query functions (upsert, search, get_by_id)
│   ├── tools/
│   │   ├── __init__.py
│   │   └── memory_tools.py    # FastMCP tool definitions (create, get, list_sectors)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models (BubbleCreate, BubbleResponse, etc.)
│   ├── __init__.py
│   └── main.py                # Alternative entry point (imports from memory_tools)
├── brainos_server.py          # ROOT-level MCP server entry point for Claude Desktop
├── run_server.py              # Alternative wrapper script
├── docker-compose.yml         # Neo4j container configuration with health checks
├── .env                       # Neo4j credentials & API keys
├── .env.example               # Environment variables template
├── .python-version            # Python version pin (3.14+)
├── pyproject.toml             # Dependency management (uv)
├── CLAUDE.md                  # Claude Code project guidance
├── claude_desktop_config_example.json  # Claude Desktop config reference
├── README.md                  # Project overview
├── error.md                   # Error logs (for debugging)
├── fastmcp_demo_app/          # FastMCP learning examples
└── docs/
    └── project/
        └── phase1/
            ├── user-stories.md      # This file
            ├── code-snippets.md     # Important code patterns
            └── phase-overview.md    # Decisions and rationale
```

---

## 4. Implemented MCP Tools

### Tool: `create_memory`
**Purpose:** Stores a new piece of information in the Synaptic Graph.

**Arguments:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `content` | str | ✅ | - | The information to remember |
| `sector` | str | ✅ | - | Cognitive sector (Episodic, Semantic, Procedural, Emotional, Reflective) |
| `source` | str | ❌ | "direct_chat" | Origin of the data (transcript, direct_chat, etc.) |
| `salience` | float | ❌ | 0.5 | Importance score (0.0 to 1.0) |

**Returns:** Formatted success message with bubble ID, sector, timestamp, and salience.

**Implementation:** Validates input → Calls `upsert_bubble` → Returns success message.

---

### Tool: `get_memory`
**Purpose:** Retrieves memories based on a keyword search.

**Arguments:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | str | ✅ | - | The search term to find matching memories |
| `limit` | int | ❌ | 10 | Maximum number of results to return (1-100) |

**Returns:** Formatted list of matching memories with ID, sector, salience, timestamp, source, and content.

**Implementation:** Calls `search_bubbles` → Formats results → Returns list to Claude.

---

### Tool: `list_sectors` ✨ NEW
**Purpose:** Lists all available cognitive sectors in the Brain OS ontology.

**Arguments:** None

**Returns:** Formatted list of the five-sector ontology with descriptions:
- **Episodic**: Events and experiences (What happened and when)
- **Semantic**: Hard facts and knowledge (Requirements, names, technical data)
- **Procedural**: Habits and workflows (The 'My Way' protocol and brand behaviors)
- **Emotional**: Sentiment and vibe (Tracking morale, frustration, excitement)
- **Reflective**: Meta-memory (Logs of how the system synthesizes information)

**Implementation:** Returns static ontology description for user reference.

---

## 5. Technical Stack & Setup

### Runtime & Dependencies
*   **Runtime:** Python 3.14+
*   **Package Manager:** `uv`
*   **Libraries:**
    *   `fastmcp>=2.14.2` - MCP server framework
    *   `neo4j>=5.25.0` - Async Neo4j driver
    *   `python-dotenv>=1.0.0` - Environment variable loading
    *   `pydantic>=2.10.0` - Data validation
    *   `groq>=0.11.0` - Fast LLM API (System 1)
    *   `openai>=1.57.0` - OpenRouter client (System 2)

### Docker Compose Configuration
Neo4j runs in a Docker container with the following configuration:
*   **Image:** `neo4j:5.25-community`
*   **Ports:** 7474 (HTTP), 7687 (Bolt)
*   **Memory:** 512m initial, 1G max heap
*   **Plugins:** APOC enabled
*   **Volumes:** Data, logs, import, and plugins persist across restarts
*   **Health Check:** HTTP endpoint polled every 10s

**Start the database:**
```bash
docker-compose up -d
```

**Neo4j Browser:** http://localhost:7474 (default: `neo4j` / `brainos_password_123`)

### Environment Variables

```env
# Neo4j (local Docker instance)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=brainos_password_123

# Groq (fast actions - System 1)
GROQ_API_KEY=<your-groq-key>
GROQ_QUICK_MODEL=openai/gpt-oss-120b

# OpenRouter (deep thinking - System 2)
OPENROUTER_API_KEY=<your-openrouter-key>
OPENROUTER_RESEARCHING_MODEL=anthropic/claude-sonnet-4
OPENROUTER_THINKINIG_MODEL=anthropic/claude-sonnet-4
OPENROUTER_CREATIVE_MODEL=anthropic/claude-sonnet-4
OPENROUTER_PLANNING_MODEL=anthropic/claude-opus-4
```

---

## 6. Running the Server

### Development (STDIO)
```bash
# Ensure Neo4j is running
docker-compose up -d

# Run the MCP server
fastmcp run brainos_server.py:mcp
```

### HTTP Transport (for testing/remote)
```bash
fastmcp run brainos_server.py:mcp --transport http --port 8000
```

### Claude Desktop Integration
```bash
# From your project directory
fastmcp install claude-desktop brainos_server.py --project . --env-file .env
```

Then restart Claude Desktop completely. Look for the hammer icon (🔨) to confirm the server loaded.

---

## 7. Bugs Fixed During Implementation

### Bug #1: Neo4j element_id Type Mismatch
**Error:** `Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='4:e087e584-a2bb-446e-9147-50a7b3f906df:0']`

**Root Cause:** Neo4j's `element_id` returns a string (e.g., `'4:e087e584-a2bb-446e-9147-50a7b3f906df:0'`), but `BubbleResponse.id` was typed as `int`.

**Fix:** Changed `BubbleResponse.id` from `int` to `str` in `src/utils/schemas.py`.

### Bug #2: Query Parameter Conflict
**Error:** `AsyncSession.run() got multiple values for argument 'query'`

**Root Cause:** In `search_bubbles()`, the Cypher parameter name `$query` conflicted with `session.run()`'s first positional parameter (also named `query`).

**Fix:** Renamed Cypher parameters to avoid conflict:
- `$query` → `$search_query`
- `$limit` → `$result_limit`

---

## 8. What's Next (Phase 2)

Phase 1 focused on core MCP tools and Neo4j integration. Phase 2 will introduce:

1. **PocketFlow Workflows:** Multi-agent orchestration using the `AsyncFlow` pattern
2. **Salience Scoring:** Automatic importance decay and reinforcement
3. **Neurochain Connections:** Relationships between bubbles with synaptic weights
4. **Cloud Generation:** AI-synthesized insights from multiple related memories
5. **Dual-LLM Integration:** Using Groq for fast classification and OpenRouter for deep synthesis

See `phase-overview.md` for detailed architectural decisions and `code-snippets.md` for key implementation patterns.