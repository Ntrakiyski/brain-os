# Phase 4: API Changes

> Track new tools, modified tools, and breaking changes for Phase 4
>
> **✅ Add-ons Implemented**: Email Notifications (4 tools) + Phoenix Cloud Observability
> **See [final-phase4-addons.md](./final-phase4-addons.md) for implemented add-on tools**
>
> **Observability Note**: Phoenix Cloud provides complete visual tracking - no custom visualization tools needed

---

## New Tools (Phase 4)

### Monitoring & Observability

#### TOOL 10: get_system_health

**Purpose**: Get comprehensive system health status

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| None | - | - | - | No parameters required |

**Returns:**
```json
{
  "neo4j": {
    "status": "healthy",
    "latency_ms": 45,
    "total_memories": 147
  },
  "llm_providers": {
    "groq": {"status": "healthy", "latency_ms": 120},
    "openrouter": {"status": "healthy", "latency_ms": 2300}
  },
  "background_tasks": [...],
  "uptime": "14 days, 6 hours"
}
```

**Implementation File:** `src/tools/monitoring/get_system_health.py`

---

#### TOOL 11: get_task_status

**Purpose**: Query status of background tasks

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task_name` | string | No | `"all"` | Task name or "all" for all tasks |

**Returns:** Human-readable task status with schedule, last run, next run, history

**Implementation File:** `src/tools/monitoring/get_task_status.py`

---

### Observability via Phoenix Cloud

**Visual tracking is handled by Phoenix Cloud dashboard** - no custom tools needed.

**What Phoenix tracks:**
- **Tool Usage**: Which tools are called, frequency, timing
- **Client Inputs**: What data comes from the client
- **System Creations**: What memories/data are created
- **Responses**: What's sent back to the client
- **LLM Calls**: All Groq and OpenRouter API calls
- **Neo4j Queries**: Database operations and performance

**See [final-phase4-addons.md](./final-phase4-addons.md) for Phoenix setup.**

---

## Modified Tools (Phase 4)

### Enhanced with Context Logging

All existing tools will be enhanced with FastMCP Context injection:

#### create_memory (ENHANCED)

**Changes:**
- Add `ctx: Context = CurrentContext()` parameter
- Emit debug logs at each step
- Emit info logs with memory details
- Emit error logs on failures

**New Behavior:**
```python
@mcp.tool
async def create_memory(
    content: str,
    sector: str,
    ...
    ctx: Context = CurrentContext()  # NEW
) -> str:
    await ctx.debug("create_memory: Starting")
    await ctx.info(f"Creating {sector} memory")
    # ... create ...
    await ctx.info("Memory stored", extra={"memory_id": id})
    return f"Memory stored: {id}"
```

**File:** `src/tools/memory/create_memory.py`

---

#### get_memory_relations (ENHANCED)

**Changes:**
- Add progress reporting (0%, 20%, 60%, 100%)
- Add debug logs for each PocketFlow node
- Add info logs with concept counts and bubble counts

**New Progress Stages:**
- 0%: Starting context analysis
- 20%: Pre-query complete
- 60%: Neo4j query complete
- 100%: Synthesis complete

**File:** `src/flows/contextual_retrieval.py`

---

#### summarize_project (ENHANCED)

**Changes:**
- Add progress reporting (0%, 30%, 80%, 100%)
- Add info logs for memory retrieval and synthesis

**New Progress Stages:**
- 0%: Starting project summary
- 30%: Memories retrieved
- 80%: LLM synthesis complete
- 100%: Formatting complete

**File:** `src/tools/agents/summarize_project.py`

---

#### get_instinctive_memory (ENHANCED)

**Changes:**
- Add debug logs for concept extraction
- Add info logs with activation count

**File:** `src/flows/instinctive_activation.py`

---

## New Background Tasks (Phase 4)

### Background Task 1: synaptic_pruning_task

**Purpose**: Daily salience decay for unused memories

**Schedule:** Every 24 hours

**Behavior:**
- Find memories not accessed in 30+ days
- Reduce salience by 10%
- Log number of memories decayed

**Implementation File:** `src/tasks/background.py`

---

### Background Task 2: cloud_synthesis_task

**Purpose**: Weekly generation of Reflective insights

**Schedule:** Every 7 days (168 hours)

**Behavior:**
- Find memory clusters with 5+ high-salience memories
- Generate Reflective cloud using OpenRouter
- Store cloud as Reflective memory
- Log number of clouds generated

**Implementation File:** `src/tasks/background.py`

---

### Background Task 3: health_check_task

**Purpose**: Hourly system health monitoring

**Schedule:** Every 60 minutes

**Behavior:**
- Check Neo4j connectivity
- Check Groq API availability
- Check OpenRouter API availability
- Store status in system memory
- Log health status

**Implementation File:** `src/tasks/background.py`

---

## New Files (Phase 4)

```
src/
├── tasks/                              # NEW
│   ├── __init__.py
│   ├── synaptic_pruning.py             # Salience decay logic
│   ├── cloud_synthesis.py              # Insight generation logic
│   └── health_monitoring.py            # Health check logic
├── tools/
│   └── monitoring/                     # NEW
│       ├── __init__.py
│       ├── get_system_health.py        # System health check tool
│       └── get_task_status.py          # Task status query tool
└── utils/
    ├── health.py                       # NEW: Health check utilities
    └── observability.py                # NEW: Phoenix Cloud integration
```

---

## Modified Files (Phase 4)

### Enhanced with Context + Progress

```
src/flows/contextual_retrieval.py        # Add Context + Progress
src/flows/instinctive_activation.py      # Add Context
src/flows/summarize_project.py           # Add Context + Progress
src/tools/memory/create_memory.py        # Add Context
src/tools/memory/get_memory.py           # Add Context
src/tools/memory/get_relations.py        # Add Context (wrapper)
src/tools/agents/summarize_project.py    # Add Context + Progress
brainos_server.py                        # Register background tasks
```

---

## FastMCP Feature Usage (Phase 4)

### Context Logging

```python
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

@mcp.tool
async def my_tool(ctx: Context = CurrentContext()):
    # Debug level - detailed execution flow
    await ctx.debug("Starting operation")

    # Info level - normal operation
    await ctx.info("Processing 5 items")

    # Warning level - potential issues
    await ctx.warning("Using fallback method")

    # Error level - failures
    await ctx.error("Operation failed", extra={"error": str(e)})

    # Structured logging with extra data
    await ctx.info("Memory stored", extra={
        "memory_id": "123",
        "sector": "Semantic"
    })
```

### Progress Reporting

```python
@mcp.tool
async def long_operation(ctx: Context = CurrentContext()):
    # Start progress
    await ctx.report_progress(progress=0, total=100)

    # Update progress
    await ctx.report_progress(progress=50, total=100)

    # Complete progress
    await ctx.report_progress(progress=100, total=100)
```

### Background Tasks

```python
@mcp.background_task(interval_hours=24)
async def my_task():
    """Run daily."""
    logger.info("Task running")
    # ... do work ...
    return result
```

---

## Breaking Changes (Phase 4)

**None** - All changes are additive. Existing tools will work as before, with enhanced logging.

---

## Migration Guide (Phase 3 → Phase 4)

### For Tool Developers

If you've created custom tools, update them to use Context:

**Before (Phase 3):**
```python
@mcp.tool
async def my_tool(param: str) -> str:
    result = await do_work(param)
    return result
```

**After (Phase 4):**
```python
@mcp.tool
async def my_tool(
    param: str,
    ctx: Context = CurrentContext()  # Add this
) -> str:
    await ctx.debug(f"Starting with param: {param}")
    result = await do_work(param)
    await ctx.info(f"Complete: {len(result)} items")
    return result
```

---

## API Compatibility Matrix

| Tool | Phase 3 | Phase 4 | Notes |
|------|---------|---------|-------|
| create_memory | ✓ | ✓ Enhanced | Added Context logging |
| get_memory | ✓ | ✓ Enhanced | Added Context logging |
| get_all_memories | ✓ | ✓ Enhanced | Added Context logging |
| list_sectors | ✓ | ✓ Enhanced | Added Context logging |
| visualize_memories | ✓ | ✓ Enhanced | Added Context logging |
| get_instinctive_memory | ✓ | ✓ Enhanced | Added Context logging |
| get_memory_relations | ✓ | ✓ Enhanced | Added Context + Progress |
| visualize_relations | ✓ | ✓ Enhanced | Added Context logging |
| summarize_project | ✓ | ✓ Enhanced | Added Context + Progress |
| delete_memory | ✓ | ✓ Enhanced | Added Context logging |
| delete_all_memories | ✓ | ✓ Enhanced | Added Context logging |
| **get_system_health** | ❌ | ✓ | **NEW** |
| **get_task_status** | ❌ | ✓ | **NEW** |
| **Phoenix Observability** | ❌ | ✓ | **Via final-phase4-addons.md** |

---

## End of Phase 4 API Changes
