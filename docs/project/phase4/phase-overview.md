# Phase 4: Observability, Background Tasks & Circadian Rhythm

> **Status**: Design Phase
> **Priority**: High
> **Start Date**: 2026-01-09
> **Estimated Complexity**: 2-3 weeks
> **Add-ons Implemented**: ✅ Email Notifications + Phoenix Cloud Observability (see [final-phase4-addons.md](./final-phase4-addons.md))

---

## Executive Summary

Phase 4 transforms Brain OS from a passive memory store into an **active, self-monitoring cognitive system** with three major breakthroughs:

1. **Observability & Monitoring**: Client-side logging via FastMCP Context for debugging and tracking
2. **Background Tasks (The Heartbeat)**: Circadian rhythm - automated maintenance cycles running in background
3. **Progress Reporting**: Real-time progress updates for long-running operations (synthesis, weekly reviews)

**Architecture Focus**: Leverage FastMCP 2.14+ features (Context logging, progress reporting, background tasks).

---

## Vision: The Living Cognitive System

> *"A brain isn't just storage - it's alive. It pulses with circadian rhythms, it self-regulates through maintenance cycles, and it provides feedback about its internal state."*

**Current Brain OS (Phase 1-3)**:
- Passive: You call tools, get results
- Opaque: No visibility into what's happening during LLM calls
- Static: No automated maintenance or background activity

**Brain OS Phase 4**:
- **Observable**: See what Brain OS is thinking (real-time logs)
- **Transparent**: Progress bars for long operations
- **Alive**: Background maintenance cycles (synaptic pruning, cloud synthesis)

---

## Phase 4 Goals

| Goal | Description | Success Metric |
|------|-------------|----------------|
| **G1: Client Logging** | All tools use FastMCP Context for logging | 100% of tools emit structured logs |
| **G2: Progress Reporting** | Long operations show real-time progress | All PocketFlow flows report progress |
| **G3: Background Tasks** | Circadian rhythm maintenance cycles | Automated background synthesis and pruning |
| **G4: Observability Tools** | Query system state, health checks | `get_system_health`, `get_task_status` tools |
| **G5: Monitoring Dashboard** | Visualize system state and metrics | `visualize_system_state` tool |

---

## Feature 1: Client Logging via FastMCP Context

### Concept

FastMCP 2.14+ provides the `Context` object for sending structured logs back to MCP clients. This gives real-time visibility into tool execution.

### PocketFlow Pattern

All PocketFlow nodes should use Context for logging:

```python
# src/flows/contextual_retrieval.py (ENHANCED)
from fastmcp.server.dependencies import get_context

class PreQueryContextNode(AsyncNode):
    async def prep_async(self, shared):
        ctx = get_context()
        await ctx.debug("PreQueryContext: Starting context analysis")

        user_input = shared.get("user_input", "")
        await ctx.info(f"Analyzing input: {user_input[:50]}...")

        return user_input, shared.get("conversation_history", [])

    async def exec_async(self, inputs):
        ctx = get_context()
        await ctx.debug("PreQueryContext: Calling Groq for concept extraction")

        # ... LLM call ...
        await ctx.info(
            f"Context analyzed: {len(context['related_concepts'])} concepts found",
            extra={
                "intent": context["intent"],
                "concepts": context["related_concepts"],
                "time_scope": context["time_scope"]
            }
        )
        return context

    async def post_async(self, shared, prep_res, context):
        ctx = get_context()
        await ctx.info("PreQueryContext: Analysis complete, proceeding to query")
        return "query"
```

### MCP Tool Pattern

```python
# src/tools/memory/create_memory.py (ENHANCED)
from fastmcp import FastMCP, Context
from fastmcp.dependencies import CurrentContext

def register_create_memory(mcp) -> None:
    @mcp.tool
    async def create_memory(
        content: str = Field(description="What to remember"),
        sector: str = Field(description="Cognitive sector"),
        ctx: Context = CurrentContext()  # Inject Context
    ) -> str:
        """Store a new memory with comprehensive logging."""
        await ctx.debug("create_memory: Starting memory creation")
        await ctx.info(f"Content length: {len(content)}, Sector: {sector}")

        try:
            # Validate
            await ctx.debug("create_memory: Validating input")
            # ... validation ...

            # Store in Neo4j
            await ctx.info("create_memory: Writing to Neo4j")
            # ... Neo4j write ...

            await ctx.info(
                "Memory stored successfully",
                extra={
                    "memory_id": result.id,
                    "sector": sector,
                    "salience": salience,
                    "memory_type": memory_type
                }
            )

            return f"Memory stored: {result.id}"

        except Exception as e:
            await ctx.error(f"Failed to create memory: {str(e)}")
            raise
```

### Log Levels

| Level | Use For | Example |
|-------|---------|---------|
| `debug` | Detailed execution flow | "Calling Groq for concept extraction" |
| `info` | Normal operation progress | "Found 5 memories, synthesizing..." |
| `warning` | Non-critical issues | "LLM fallback activated, using basic extraction" |
| `error` | Failures needing attention | "Neo4j connection timeout" |

---

## Feature 2: Progress Reporting

### Concept

Long-running operations (PocketFlow flows with LLM calls) should report progress so users see real-time updates.

### Progress in PocketFlow

```python
# src/flows/contextual_retrieval.py (ENHANCED)
class PostQuerySynthesizeNode(AsyncNode):
    async def exec_async(self, inputs):
        ctx = get_context()
        bubbles, relations, context = inputs

        # Report progress: 0% starting
        await ctx.report_progress(progress=0, total=100)
        await ctx.info("Starting synthesis with OpenRouter")

        if not bubbles:
            await ctx.report_progress(progress=100, total=100)
            return {"summary": "No memories found", "bubbles": []}

        # 20% - Bubbles formatted
        bubble_text = "\n".join([f"[{i}] {b['sector']}: {b['content'][:100]}..."
                                 for i, b in enumerate(bubbles[:15])])
        await ctx.report_progress(progress=20, total=100)

        # 40% - Calling LLM
        await ctx.info("Calling OpenRouter for synthesis")
        client = get_openrouter_client()

        response = await client.chat.completions.create(...)
        await ctx.report_progress(progress=60, total=100)

        # 80% - Parsing response
        import json
        synthesis = json.loads(response.choices[0].message.content)
        synthesis["bubbles"] = bubbles
        await ctx.report_progress(progress=80, total=100)

        # 100% - Complete
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Synthesis complete: {len(synthesis.get('themes', []))} themes")

        return synthesis
```

### Multi-Stage Progress

```python
# src/tools/agents/summarize_project.py (ENHANCED)
@mcp.tool
async def summarize_project(
    project: str = Field(description="Project name"),
    limit: int = Field(default=20),
    ctx: Context = CurrentContext()
) -> str:
    """Summarize with multi-stage progress reporting."""

    # Stage 1: Memory retrieval (0-30%)
    await ctx.info(f"Retrieving memories for {project}")
    memories = await search_bubbles(project, limit)
    await ctx.report_progress(progress=30, total=100)

    # Stage 2: LLM synthesis (30-80%)
    await ctx.info(f"Synthesizing {len(memories)} memories with AI")
    summary = await run_llm_synthesis(memories)
    await ctx.report_progress(progress=80, total=100)

    # Stage 3: Formatting (80-100%)
    await ctx.info("Formatting summary")
    formatted = format_summary(summary)
    await ctx.report_progress(progress=100, total=100)

    return formatted
```

---

## Feature 3: Background Tasks (The Heartbeat)

### Concept

Brain OS should run automated maintenance cycles in the background:
- **Synaptic Pruning**: Decay salience of old, unused memories
- **Cloud Synthesis**: Generate Reflective insights from memory clusters
- **Health Monitoring**: Check Neo4j connection, LLM API status

### FastMCP Background Tasks

```python
# src/tasks/background.py
import asyncio
from datetime import datetime
from fastmcp import FastMCP

def register_background_tasks(mcp: FastMCP) -> None:
    """Register all background maintenance tasks."""

    @mcp.background_task(interval_hours=24)
    async def synaptic_pruning_task():
        """Daily salience decay for unused memories."""
        from src.database.connection import get_driver
        from src.database.queries.memory import decay_unused_salience

        logger = logging.getLogger(__name__)
        driver = await get_driver()

        logger.info("Starting synaptic pruning cycle")

        # Decay memories not accessed in 30 days
        decayed = await decay_unused_salience(
            driver,
            days_inactive=30,
            decay_rate=0.1  # Reduce salience by 10%
        )

        logger.info(f"Synaptic pruning complete: {decayed} memories decayed")

    @mcp.background_task(interval_hours=168)  # Weekly
    async def cloud_synthesis_task():
        """Weekly synthesis of memory clusters into insights."""
        from src.flows.synthesis import generate_clouds

        logger = logging.getLogger(__name__)

        logger.info("Starting cloud synthesis cycle")

        # Find memory clusters with high salience
        # Generate Reflective cloud memories
        clouds = await generate_clouds()

        logger.info(f"Cloud synthesis complete: {len(clouds)} insights generated")

    @mcp.background_task(interval_minutes=60)
    async def health_check_task():
        """Hourly health monitoring."""
        from src.utils.health import check_neo4j, check_llm_apis

        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "neo4j": await check_neo4j(),
            "groq": await check_llm_apis("groq"),
            "openrouter": await check_llm_apis("openrouter")
        }

        # Store status in system memory for querying
        await store_system_status(status)

        logger.info(f"Health check: {status}")
```

### Task Status Querying

```python
# src/tools/monitoring/get_task_status.py
@mcp.tool
async def get_task_status(
    task_name: str = Field(description="Task name or 'all' for all tasks")
) -> str:
    """Query status of background tasks."""

    if task_name == "all":
        tasks = await get_all_task_status()
    else:
        tasks = [await get_task_status(task_name)]

    output = ["## Background Task Status\n"]

    for task in tasks:
        output.append(f"### {task['name']}")
        output.append(f"- Status: {task['status']}")
        output.append(f"- Last run: {task['last_run']}")
        output.append(f"- Next run: {task['next_run']}")
        output.append(f"- Last result: {task['last_result']}")

    return "\n".join(output)
```

---

## Feature 4: Observability Tools

### Tool: get_system_health

```python
# src/tools/monitoring/get_system_health.py
@mcp.tool
async def get_system_health(
    ctx: Context = CurrentContext()
) -> str:
    """Get comprehensive system health status."""

    await ctx.info("Collecting system health metrics")

    health = {
        "neo4j": await check_neo4j_health(),
        "llm_providers": {
            "groq": await check_groq_health(),
            "openrouter": await check_openrouter_health()
        },
        "memory_stats": await get_memory_statistics(),
        "background_tasks": await get_all_task_status(),
        "uptime": await get_uptime()
    }

    return format_health_report(health)
```

### Tool: visualize_system_state

```python
# src/tools/monitoring/visualize_system_state.py
@mcp.tool
async def visualize_system_state(
    format: str = Field(default="ascii", description="ascii or json")
) -> str:
    """Visualize current system state."""

    stats = await get_comprehensive_stats()

    if format == "json":
        return json.dumps(stats, indent=2)

    # ASCII visualization
    lines = []
    lines.append("Brain OS System State")
    lines.append("=" * 50)
    lines.append(f"Uptime: {stats['uptime']}")
    lines.append(f"Total Memories: {stats['total_memories']}")
    lines.append("")
    lines.append("Memory Distribution:")
    for sector, count in stats['sectors'].items():
        bar = "█" * int(count / stats['total_memories'] * 50)
        lines.append(f"  {sector}: {bar} {count}")
    lines.append("")
    lines.append("Background Tasks:")
    for task in stats['tasks']:
        status_icon = "✓" if task['status'] == "healthy" else "✗"
        lines.append(f"  {status_icon} {task['name']}: {task['status']}")

    return "\n".join(lines)
```

---

## Implementation Plan

### Week 1: Logging Foundation
- [ ] Add `Context` injection to all memory tools
- [ ] Implement structured logging in create_memory
- [ ] Implement structured logging in get_memory_relations
- [ ] Implement structured logging in summarize_project
- [ ] Test logging output in Claude Desktop

### Week 2: Progress Reporting
- [ ] Add progress reporting to contextual_retrieval flow
- [ ] Add progress reporting to summarize_project flow
- [ ] Add progress reporting to instinctive_activation flow
- [ ] Test progress bars in Claude Desktop

### Week 3: Background Tasks
- [ ] Implement synaptic_pruning_task
- [ ] Implement cloud_synthesis_task
- [ ] Implement health_check_task
- [ ] Create get_task_status tool
- [ ] Create get_system_health tool
- [ ] Test background task scheduling

---

## File Structure (Phase 4)

```
0brainos/
├── src/
│   ├── tasks/                     # NEW: Background tasks
│   │   ├── __init__.py
│   │   ├── synaptic_pruning.py    # Salience decay cycle
│   │   ├── cloud_synthesis.py     # Insight generation cycle
│   │   └── health_monitoring.py   # System health checks
│   ├── tools/
│   │   └── monitoring/            # NEW: Observability tools
│   │       ├── __init__.py
│   │       ├── get_system_health.py
│   │       ├── get_task_status.py
│   │       └── visualize_system_state.py
│   ├── utils/
│   │   └── health.py              # NEW: Health check utilities
│   └── flows/
│       └── *.py                   # ENHANCED: Add Context + Progress
├── docs/
│   └── project/
│       └── phase4/
│           ├── phase-overview.md  # This file
│           ├── user-stories.md
│           └── api-changes.md
└── brainos_server.py              # ENHANCED: Register background tasks
```

---

## Success Criteria

| Criterion | How to Measure | Target |
|-----------|----------------|--------|
| **Logging Coverage** | % of tools with Context logging | 100% of tools emit logs |
| **Progress Visibility** | Long operations report progress | All flows >2s report progress |
| **Background Tasks** | Automated maintenance runs | 3 tasks running (pruning, synthesis, health) |
| **Observability** | System state queryable | get_system_health works |
| **Performance** | Logging overhead | <5% latency increase |

---

## Open Questions

1. **Background Task Storage**: Where to store task status?
   - **Proposal**: Neo4j with `TaskStatus` nodes, or in-memory cache

2. **Synaptic Pruning Rate**: How aggressive should salience decay be?
   - **Proposal**: 10% decay per month for unused memories

3. **Cloud Synthesis Trigger**: When to auto-generate insights?
   - **Proposal**: Weekly cycle, clusters with >5 high-salience memories

4. **Progress Granularity**: How often to report progress?
   - **Proposal**: 5-10 updates per operation (0%, 20%, 40%, ..., 100%)

---

## Next Steps

1. **Review this document** with feedback
2. **Create user-stories.md** with concrete scenarios
3. **Start Week 1**: Add Context logging to all tools
4. **Test observability** in Claude Desktop

---

**End of Phase 4 Overview**
