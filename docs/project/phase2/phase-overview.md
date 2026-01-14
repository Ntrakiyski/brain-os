# Phase 2: Modular Architecture & First PocketFlow Agent

> **Purpose:** Establish scalable folder structure and build the first configurable PocketFlow agent as a pattern for 20+ future agents.

---

## Executive Summary

Phase 2 is a **foundation sprint** focused on:
1. Refactoring to modular folder structure (scales to 70+ tools)
2. Installing PocketFlow framework
3. Building ONE reference agent (`summarize_project`) that demonstrates the pattern for all future agents

**Design Philosophy:** Every agent/tool follows the same configurable pattern. Changes happen via config, not code.

---

## Target Structure (Phase 2) - IMPLEMENTED

```
0brainos/
├── brainos_server.py              # Minimal entry point (65 lines)
├── src/
│   ├── core/
│   │   └── config.py              # Existing: Neo4j, Groq, OpenRouter configs
│   ├── database/
│   │   ├── connection.py          # Existing: Neo4j async driver
│   │   └── queries/               # NEW: Modular query organization
│   │       ├── __init__.py        # Public API exports
│   │       └── memory.py          # Moved: Bubble CRUD operations
│   ├── tools/                     # NEW: Modular tool structure
│   │   ├── __init__.py            # Exports: register_memory_tools, register_agent_tools
│   │   ├── memory/                # Refactored from single file
│   │   │   ├── __init__.py        # register_memory_tools()
│   │   │   ├── create.py          # create_memory tool (82 lines)
│   │   │   ├── get.py             # get_memory, get_all_memories (86 lines)
│   │   │   ├── list.py            # list_sectors tool (19 lines)
│   │   │   └── visualize.py       # visualize_memories tool (115 lines)
│   │   └── agents/                # NEW: Agent-based tools
│   │       ├── __init__.py        # register_agent_tools()
│   │       └── summarize_project.py  # summarize_project tool (70 lines)
│   ├── agents/                    # NEW: Agent layer (separate from tools)
│   │   ├── __init__.py            # Exports: BaseAgent, AgentConfig
│   │   ├── base.py                # BaseAgent class (170 lines)
│   │   └── summarize_project.py   # SummarizeProjectAgent (25 lines)
│   └── utils/
│       ├── schemas.py             # Existing: Pydantic models
│       └── llm.py                 # NEW: LLM client factory (120 lines)
```

---

## The Agent Pattern (As Implemented)

Every agent follows this structure:

```python
# src/agents/summarize_project.py
from src.agents.base import BaseAgent, AgentConfig, OutputFormat

class SummarizeProjectAgent(BaseAgent):
    """
    Agent that summarizes project-related memories.

    Configuration can be modified without changing code:
    - Change the model (provider/task)
    - Adjust the prompt template
    - Modify output format
    - Set temperature and token limits
    """

    config = AgentConfig(
        name="summarize_project",
        model="openrouter/creative",           # Format: "provider/task"
        prompt_template="""...""",             # With {placeholders}
        output_format=OutputFormat.MARKDOWN,   # or JSON, TEXT
        temperature=0.7,
        max_tokens=2000,
        system_prompt="You are a helpful assistant..."
    )

# Usage: await SummarizeProjectAgent.run(project="Brain OS", memories="...")
```

**Key Principle:** To change behavior, modify `config`. Never touch the agent code.

### Configuration Options

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Unique agent identifier |
| `model` | str | `"provider/task"` format |
| `prompt_template` | str | Template with `{placeholder}` variables |
| `output_format` | OutputFormat | `TEXT`, `MARKDOWN`, or `JSON` |
| `temperature` | float | 0.0 (deterministic) to 1.0 (creative) |
| `max_tokens` | int | Response length limit |
| `system_prompt` | str \| None | Optional LLM system prompt |
| `timeout_seconds` | int | Request timeout (default: 30) |

---

## Implementation Steps

### Step 1: Refactor Database Queries
- Move `queries.py` → `queries/memory.py`
- Update imports

### Step 2: Refactor Tools
- Move `memory_tools.py` → `tools/memory/*.py`
- Split into `create.py`, `get.py`, `visualize.py`
- Create registration pattern

### Step 3: Install PocketFlow
```bash
uv add pocketflow
```

### Step 4: Create Base Agent Pattern
- `src/agents/base.py`: Reusable agent class
- Configuration-driven execution
- Standardized input/output

### Step 5: Build `summarize_project` Agent
- Query memories by project keyword
- Send to LLM with configured prompt
- Return structured summary

### Step 6: Register as MCP Tool
- Expose via `@mcp.tool`
- Test end-to-end

---

## Success Criteria

- [x] Modular folder structure in place
- [x] All 5 existing tools still work after refactor
- [x] PocketFlow installed and working
- [x] `summarize_project` agent functional
- [x] Agent config changeable without code modification
- [x] Pattern documented for next 19 agents

---

## Files to Create/Modify

| File | Action | Lines |
|------|--------|-------|
| `src/database/queries/__init__.py` | Create | ~5 |
| `src/database/queries/memory.py` | Move from `queries.py` | ~170 |
| `src/tools/__init__.py` | Update | ~10 |
| `src/tools/memory/__init__.py` | Create | ~15 |
| `src/tools/memory/create.py` | Extract from `memory_tools.py` | ~80 |
| `src/tools/memory/get.py` | Extract from `memory_tools.py` | ~70 |
| `src/tools/memory/visualize.py` | Extract from `memory_tools.py` | ~100 |
| `src/tools/memory/list.py` | Extract from `memory_tools.py` | ~20 |
| `src/tools/agents/__init__.py` | Create | ~15 |
| `src/tools/agents/summarize_project.py` | Create | ~70 |
| `src/utils/llm.py` | Create | ~120 |
| `src/agents/__init__.py` | Create | ~5 |
| `src/agents/base.py` | Create | ~170 |
| `src/agents/summarize_project.py` | Create | ~25 |
| `brainos_server.py` | Update imports | ~65 |

---

## How to Add New Agents (The 3-Step Pattern)

After this phase, adding new agents follows a consistent 3-step process:

### Step 1: Create the Agent Class
```python
# src/agents/my_agent.py
from src.agents.base import BaseAgent, AgentConfig, OutputFormat

class MyAgent(BaseAgent):
    config = AgentConfig(
        name="my_agent",
        model="groq/quick",                  # or "openrouter/creative"
        prompt_template="Process: {input}",   # {variables} get substituted
        output_format=OutputFormat.JSON,
        temperature=0.3,
        max_tokens=1000
    )
```

### Step 2: Create the MCP Tool Wrapper
```python
# src/tools/agents/my_agent.py
from pydantic import Field
from src.agents.my_agent import MyAgent
from src.database.queries.memory import search_bubbles

def register_my_agent(mcp) -> None:
    @mcp.tool
    async def my_tool(
        input: str = Field(description="Input to process")
    ) -> str:
        result = await MyAgent.run(input=input)
        return f"Result: {result}"
```

### Step 3: Register the Tool
```python
# src/tools/agents/__init__.py
from src.tools.agents.my_agent import register_my_agent

def register_agent_tools(mcp) -> None:
    register_summarize_project(mcp)
    register_my_agent(mcp)  # Add this line
```

**That's it!** No changes to `brainos_server.py` needed.

---

## LLM Utility Implementation

The `src/utils/llm.py` module provides factory functions for LLM clients:

### Supported Providers

| Provider | Function | Use Case | Speed |
|----------|----------|----------|-------|
| Groq | `get_groq_client()` | Fast classification, extraction | ~100ms |
| OpenRouter | `get_openrouter_client()` | Deep thinking, synthesis | ~3-10s |

### Model Resolution

```python
# Agent config uses shorthand
model="openrouter/creative"

# Resolved to actual model via environment:
OPENROUTER_CREATIVE_MODEL=anthropic/claude-sonnet-4
```

### Available Model Tasks

| Provider | Task | Env Variable | Default Model |
|----------|------|--------------|---------------|
| Groq | quick | GROG_QUICK_MODEL | openai/gpt-oss-120b |
| OpenRouter | creative | OPENROUTER_CREATIVE_MODEL | claude-sonnet-4 |
| OpenRouter | researching | OPENROUTER_RESEARCHING_MODEL | claude-sonnet-4 |
| OpenRouter | planning | OPENROUTER_PLANNING_MODEL | claude-opus-4 |

### Client Caching

Both `get_groq_client()` and `get_openrouter_client()` use `@lru_cache(maxsize=1)` for efficient reuse.

---

## Phase 2: ✅ COMPLETED

**Date Completed:** 2025-01-09

### Summary of Changes

1. **Modular Folder Structure Created**
   - Database queries moved to `src/database/queries/memory.py`
   - Tools split into `src/tools/memory/*.py` (create, get, visualize, list)
   - Agent tools in `src/tools/agents/`
   - Agents in `src/agents/`

2. **PocketFlow Installed**
   - Added `pocketflow==0.0.3` to dependencies
   - Note: Created custom BaseAgent pattern instead of using PocketFlow directly
   - PocketFlow available for future workflow orchestration needs

3. **LLM Utility Created**
   - `src/utils/llm.py` with Groq and OpenRouter client factories
   - Configuration-driven LLM selection
   - Model resolution via environment variables
   - Client caching with `@lru_cache`

4. **Base Agent Pattern Implemented**
   - `src/agents/base.py` with `BaseAgent` class (170 lines)
   - Configuration-driven execution via `AgentConfig` (frozen dataclass)
   - Support for multiple LLM providers (Groq, OpenRouter)
   - Support for multiple output formats (TEXT, MARKDOWN, JSON)
   - Automatic model resolution from shorthand notation

5. **First Agent Built**
   - `SummarizeProjectAgent` that retrieves project memories and generates AI summaries
   - Exposed as MCP tool `summarize_project`
   - Configuration in `src/agents/summarize_project.py`
   - Tool wrapper in `src/tools/agents/summarize_project.py`

6. **brainos_server.py Simplified**
   - Reduced from 154 lines to 65 lines
   - All inline tool definitions moved to modules
   - Clean registration pattern: `register_memory_tools(mcp)`, `register_agent_tools(mcp)`

### Tools Status

| Tool | Status | Location | Description |
|------|--------|----------|-------------|
| create_memory | ✅ Working | `src/tools/memory/create.py` | Store memories in Neo4j |
| get_memory | ✅ Working | `src/tools/memory/get.py` | Search memories by keyword |
| get_all_memories | ✅ Working | `src/tools/memory/get.py` | Retrieve all memories |
| list_sectors | ✅ Working | `src/tools/memory/list.py` | List five cognitive sectors |
| visualize_memories | ✅ Working | `src/tools/memory/visualize.py` | Generate ASCII visualizations |
| summarize_project | ✅ **NEW** | `src/tools/agents/summarize_project.py` | AI-powered project summaries |

### Next Phase (Phase 3)

With the modular foundation in place, Phase 3 can rapidly add:

**New Agents** (using the 3-step pattern):
- `classify_text_agent`: Auto-classify text into cognitive sectors (Groq)
- `extract_entities_agent`: Extract names, dates, locations (Groq)
- `generate_cloud_agent`: Synthesize insights from memory clusters (OpenRouter)

**Background Tasks**:
- Salience decay scheduler
- Memory maintenance cycles
- Cloud synthesis triggers

**Database Features**:
- Neurochain relationship queries
- Synaptic weight calculations
- Connection strength tracking

Each addition requires ~50-100 lines following established patterns.

---

## Files Created/Modified in Phase 2

### New Files Created (11 files)
```
src/database/queries/
├── __init__.py                    # 9 lines
└── memory.py                      # 171 lines (moved from queries.py)

src/tools/memory/
├── __init__.py                    # 20 lines
├── create.py                      # 82 lines (extracted)
├── get.py                         # 86 lines (extracted)
├── list.py                        # 19 lines (extracted)
└── visualize.py                   # 115 lines (extracted)

src/tools/agents/
├── __init__.py                    # 18 lines
└── summarize_project.py           # 70 lines

src/agents/
├── __init__.py                    # 7 lines
├── base.py                        # 170 lines
└── summarize_project.py           # 25 lines

src/utils/
└── llm.py                         # 120 lines

docs/project/phase2/
├── user-stories.md                # 250 lines
└── phase-overview.md              # This file
```

### Files Modified (2 files)
```
brainos_server.py                  # 154 → 65 lines (-89 lines)
src/tools/__init__.py              # 2 → 9 lines (+7 lines)
```

### Files Deleted (1 file)
```
src/tools/memory_tools.py          # 290 lines (refactored into 4 files)
src/database/queries.py            # 171 lines (moved to queries/memory.py)
```

### Total Impact
- **Lines Added**: ~1,082
- **Lines Removed**: ~464
- **Net Change**: +618 lines
- **Files Created**: 13
- **Files Modified**: 2
- **Files Deleted**: 2

---

**End of Phase 2 Documentation**
