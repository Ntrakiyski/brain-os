# Phase 2: User Stories

> **Purpose:** Define user-facing requirements and acceptance criteria for Phase 2 implementation.

---

## Overview

Phase 2 focuses on establishing a scalable foundation for Brain OS. The primary user value is making the system **configurable and extensible** - enabling rapid addition of new agents and tools without code changes.

### Target Users
- **Developer/Power User**: Adding new capabilities to Brain OS
- **End User (via Claude Desktop)**: Using the new AI-powered summarize feature

---

## Story 1: Modular Tool Organization

**As a** developer maintaining Brain OS,
**I want** tools organized in separate files by function,
**So that** I can quickly locate and modify specific functionality without scrolling through 300+ line files.

### Acceptance Criteria
- [x] Each tool resides in its own file
- [x] Related tools are grouped in subfolders (memory/, agents/)
- [x] Registration follows a consistent pattern (`register_*_tools(mcp)`)
- [x] No single file exceeds 150 lines
- [x] `brainos_server.py` is minimal (< 70 lines)

### File Structure
```
src/tools/
├── memory/
│   ├── create.py       # create_memory tool
│   ├── get.py          # get_memory, get_all_memories
│   ├── list.py         # list_sectors
│   └── visualize.py    # visualize_memories
└── agents/
    └── summarize_project.py  # summarize_project tool
```

---

## Story 2: Configuration-Driven Agent Behavior

**As a** developer extending Brain OS,
**I want** to modify agent behavior through configuration files,
**So that** I can adjust prompts, models, and output formats without touching code.

### Acceptance Criteria
- [x] Agent behavior defined in `AgentConfig` dataclass
- [x] Supported config options:
  - `name`: Unique agent identifier
  - `model`: LLM provider and task (e.g., "openrouter/creative")
  - `prompt_template`: Prompt with `{placeholders}`
  - `output_format`: text/markdown/json
  - `temperature`: 0.0-1.0
  - `max_tokens`: Response length limit
  - `system_prompt`: Optional context
- [x] Changing config requires zero code changes
- [x] Config is frozen (immutable at runtime)

### Example
```python
# To change behavior, only modify this section:
config = AgentConfig(
    name="summarize_project",
    model="openrouter/creative",      # Change: "groq/quick" for speed
    prompt_template="...",            # Change: Modify prompt
    temperature=0.7,                  # Change: 0.0 for deterministic
    output_format=OutputFormat.MARKDOWN
)
```

---

## Story 3: AI-Powered Project Summarization

**As a** Claude Desktop user,
**I want** to get a structured summary of all memories related to a project,
**So that** I can quickly review project context without reading through individual memories.

### Acceptance Criteria
- [x] Tool: `summarize_project(project="Brain OS", limit=20)`
- [x] Searches memories by project keyword
- [x] Returns structured Markdown with:
  - Overview
  - Key Decisions
  - Action Items
  - Notes
- [x] Indicates source memory count
- [x] Handles "no memories found" gracefully
- [x] Returns error message if LLM call fails

### Example Usage
```
User: "Summarize the Brain OS project"

Brain OS: # Project Summary: Brain OS
**Source:** 15 memories analyzed

## Overview
Brain OS is a cognitive operating system...

## Key Decisions
- Chose Neo4j for graph-native operations...
- Selected FastMCP for MCP server...

## Action Items
- [ ] Implement salience decay
- [ ] Add neurochain connections

## Notes
- Dual-LLM strategy: Groq for fast, OpenRouter for deep...
```

---

## Story 4: Multi-LLM Support

**As a** developer optimizing for cost/speed,
**I want** to choose between Groq (fast/cheap) and OpenRouter (deep/expensive),
**So that** I can balance response quality with cost.

### Acceptance Criteria
- [x] `src/utils/llm.py` provides both clients
- [x] Model format: `"provider/task"` (e.g., "openrouter/creative")
- [x] Groq tasks: "quick" (default model)
- [x] OpenRouter tasks: "researching", "creative", "planning"
- [x] Automatic model name resolution from environment variables
- [x] Client caching (lru_cache) for efficiency

### Supported Models
| Provider | Task | Model | Speed | Use Case |
|----------|------|-------|-------|----------|
| Groq | quick | gpt-oss-120b | ~100ms | Classification, extraction |
| OpenRouter | creative | claude-sonnet-4 | ~3s | Synthesis, writing |
| OpenRouter | researching | claude-sonnet-4 | ~5s | Research, analysis |
| OpenRouter | planning | claude-opus-4 | ~10s | Complex planning |

---

## Story 5: Database Query Modularity

**As a** developer adding new database operations,
**I want** queries organized by domain (memory, connections, clouds),
**So that** I can find and extend specific query types.

### Acceptance Criteria
- [x] `src/database/queries/` folder created
- [x] `memory.py` contains all bubble-related queries
- [x] `__init__.py` exports query functions
- [x] Queries remain async and type-annotated
- [x] No breaking changes to existing imports

### Structure
```
src/database/queries/
├── __init__.py           # Public API exports
└── memory.py             # upsert_bubble, search_bubbles, get_all_bubbles, get_bubble_by_id
```

---

## Story 6: Agent Registration Pattern

**As a** developer adding new agents,
**I want** a consistent pattern for registering agents as MCP tools,
**So that** adding agents follows a predictable 3-step process.

### Acceptance Criteria
- [x] Agent class in `src/agents/` inherits from `BaseAgent`
- [x] Tool wrapper in `src/tools/agents/` registers via `@mcp.tool`
- [x] Registration function added to `src/tools/agents/__init__.py`
- [x] `brainos_server.py` imports and calls `register_agent_tools(mcp)`

### 3-Step Pattern
```python
// Step 1: Create agent (src/agents/my_agent.py)
class MyAgent(BaseAgent):
    config = AgentConfig(...)

// Step 2: Create tool wrapper (src/tools/agents/my_agent.py)
@mcp.tool
async def my_tool(...) -> str:
    return await MyAgent.run(...)

// Step 3: Register (src/tools/agents/__init__.py)
from src.tools.agents.my_agent import register_my_agent
def register_agent_tools(mcp):
    register_my_agent(mcp)
```

---

## Non-Functional Requirements

### Performance
- [x] Tool registration adds < 100ms startup time
- [x] LLM client caching reduces initialization overhead
- [x] No impact on existing tool performance

### Maintainability
- [x] Max file length: 150 lines (except base.py at 170)
- [x] Clear separation: tools (MCP layer) vs agents (logic layer)
- [x] Type hints throughout
- [x] Docstrings on all public functions

### Extensibility
- [x] Adding new agent: ~50 lines of code (config + wrapper)
- [x] Changing agent behavior: 1 config line
- [x] Support for future LLM providers via `src/utils/llm.py`

### Backward Compatibility
- [x] All 5 existing tools work unchanged
- [x] Existing imports from `src.database.queries` still work
- [x] `brainos_server.py` endpoint at same port (9131)
- [x] Health check endpoint unchanged

---

## Definition of Done

Phase 2 is complete when:
- [x] All 6 user stories have passing acceptance criteria
- [x] Code follows the modular structure defined in Story 1
- [x] `summarize_project` tool works end-to-end with real LLM calls
- [x] Developer can add a new agent following the 3-step pattern in < 30 minutes
- [x] All existing tools still work after refactoring
- [x] Documentation updated (phase-overview.md, user-stories.md)

---

## Future Phase Considerations

These stories are **out of scope** for Phase 2 but informed the design:
- Background task execution (FastMCP background_tasks)
- Salience decay automation
- Neurochain relationship management
- Cloud synthesis workflows

The modular foundation established in Phase 2 enables these features to be added as separate agents/tools without structural changes.
