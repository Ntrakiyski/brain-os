# Phase 4: User Stories

> Concrete scenarios and workflows for observability, background tasks, and progress reporting
>
> **✅ Add-ons Implemented**: Email Notifications (4 tools) + Phoenix Cloud Observability
> **See [final-phase4-addons.md](./final-phase4-addons.md) for implemented add-on features**

---

## Story 1: The Long Synthesis

**As a** Brain OS user
**I want** to see real-time progress during long-running operations
**So that** I know the system is working and how long it will take

### Scenario

```
User: "Summarize Project A for me"

# Phase 3 (current):
# ... 8 seconds of silence ...
# Result appears with no feedback

# Phase 4 (with progress):
[INFO] Retrieving memories for Project A...
[INFO] Found 23 memories, preparing synthesis
[INFO] Calling OpenRouter for deep synthesis...
[INFO] Synthesis complete: 3 themes identified
# Result appears
```

### Technical Implementation

```python
# src/tools/agents/summarize_project.py
@mcp.tool
async def summarize_project(
    project: str,
    ctx: Context = CurrentContext()
) -> str:
    # Progress: 0%
    await ctx.info(f"Starting project summary: {project}")
    await ctx.report_progress(progress=0, total=100)

    # Progress: 20%
    memories = await search_bubbles(project)
    await ctx.info(f"Found {len(memories)} memories for {project}")
    await ctx.report_progress(progress=20, total=100)

    # Progress: 40%
    await ctx.info("Preparing LLM synthesis")
    await ctx.report_progress(progress=40, total=100)

    # Progress: 70%
    summary = await run_synthesis(memories)
    await ctx.info("LLM synthesis complete")
    await ctx.report_progress(progress=70, total=100)

    # Progress: 100%
    await ctx.info("Formatting summary")
    formatted = format_summary(summary)
    await ctx.report_progress(progress=100, total=100)

    return formatted
```

### Acceptance Criteria

- [ ] User sees info logs during summarize_project
- [ ] Progress bar updates at least 4 times (0%, 20%, 70%, 100%)
- [ ] Total operation time <10 seconds
- [ ] No timeout errors on large projects (100+ memories)

---

## Story 2: The Debugging Session

**As a** developer troubleshooting Brain OS
**I want** to see detailed logs of what's happening inside tools
**So that** I can diagnose issues quickly

### Scenario

```
User: "Why isn't get_memory_relations returning anything?"

# Phase 4 shows:
[DEBUG] PreQueryContext: Starting context analysis
[DEBUG] Input: "database decisions"
[INFO] Analyzing input: database decisions
[DEBUG] Calling Groq for concept extraction
[INFO] Context analyzed: 3 concepts found
  - intent: "search"
  - concepts: ["database", "decisions", "technology"]
  - time_scope: "all_time"
[DEBUG] ContextualQuery: Building Cypher query
[INFO] Query complete: 0 bubbles retrieved
[DEBUG] PostQuerySynthesize: No bubbles, returning early

# Developer can see: The query found 0 bubbles
# The issue might be: search terms, Neo4j data, or filters
```

### Technical Implementation

```python
# src/flows/contextual_retrieval.py
class ContextualQueryNode(AsyncNode):
    async def exec_async(self, inputs):
        ctx = get_context()

        await ctx.debug("ContextualQuery: Building dynamic Cypher")

        # Build query...
        await ctx.debug(f"Query: {query[:100]}...")
        await ctx.debug(f"Params: {params}")

        async with driver.session() as session:
            result = await session.run(query, **params)

            await ctx.debug("ContextualQuery: Executing Neo4j query")
            bubbles = []
            async for record in result:
                bubbles.append(record["b"])

        await ctx.info(f"Query complete: {len(bubbles)} bubbles retrieved")

        if len(bubbles) == 0:
            await ctx.warning(
                "No memories found - check search terms and filters",
                extra={"query": query, "params": params}
            )

        return {"bubbles": bubbles, "relations": []}
```

### Acceptance Criteria

- [ ] All PocketFlow nodes emit debug logs
- [ ] Logs show what LLM was called (Groq vs OpenRouter)
- [ ] Logs show Neo4j query and result count
- [ ] Warning logs when no results found
- [ ] Error logs with stack traces on exceptions

---

## Story 3: The Set-and-Forget Maintenance

**As a** Brain OS user
**I want** the system to automatically maintain itself
**So that** I don't have to manually prune or synthesize memories

### Scenario

```
# User doesn't do anything - system runs automatically

# Week 1:
[BACKGROUND] Synaptic pruning complete: 15 memories decayed
  - Old meeting notes: 8 memories (salience 0.8 → 0.72)
  - Temporary tasks: 7 memories (salience 0.4 → 0.36)

# Week 2:
[BACKGROUND] Cloud synthesis complete: 3 insights generated
  - Cloud: "FastTrack project shows pattern of scope creep"
  - Cloud: "Decision quality improves with external review"
  - Cloud: "N8N workflow automation saves 5h/week"

# User checks:
User: "Show me the clouds you created this week"
# → Returns 3 Reflective memories
```

### Technical Implementation

```python
# src/tasks/background.py
@mcp.background_task(interval_hours=168)  # Weekly
async def cloud_synthesis_task():
    """Generate insights from memory clusters."""
    from src.flows.synthesis import generate_clouds
    from src.database.connection import get_driver

    driver = await get_driver()

    # Find high-salience memory clusters
    clusters = await find_salience_clusters(driver, threshold=0.7, min_size=5)

    clouds_generated = []

    for cluster in clusters:
        # Generate Reflective insight using OpenRouter
        cloud = await generate_cloud(cluster)
        clouds_generated.append(cloud)

        # Store as Reflective memory
        await store_cloud(driver, cloud)

    logger.info(f"Cloud synthesis: {len(clouds_generated)} insights generated")
    return clouds_generated
```

### Acceptance Criteria

- [ ] Synaptic pruning runs weekly (decays unused memories)
- [ ] Cloud synthesis runs weekly (generates insights)
- [ ] Health check runs hourly (monitors system)
- [ ] Tasks log their completion
- [ ] User can query task status

---

## Story 4: The System Health Check

**As a** Brain OS user
**I want** to see if the system is healthy
**So that** I can trust the results it gives me

### Scenario

```
User: "Is Brain OS working properly?"

# Phase 4 response:
## System Health Status

### Neo4j Database
  Status: ✓ Healthy
  Connection: bolt://localhost:7687
  Total Memories: 147
  Response Time: 45ms

### LLM Providers
  Groq: ✓ Healthy (response: 120ms)
  OpenRouter: ✓ Healthy (response: 2.3s)

### Background Tasks
  Synaptic Pruning: Last run 2 days ago, Next run in 5 days
  Cloud Synthesis: Last run 6 days ago, Next run in 1 day
  Health Check: Running (last: 30 min ago)

### System
  Uptime: 14 days, 6 hours
  Memory Usage: 245MB
  CPU: 2.3%
```

### Technical Implementation

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

async def check_neo4j_health():
    """Check Neo4j connectivity and response time."""
    import time
    from src.database.connection import get_driver

    driver = await get_driver()

    start = time.time()
    try:
        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            await result.single()
        latency = (time.time() - start) * 1000

        count = await get_total_memory_count(driver)

        return {
            "status": "healthy",
            "latency_ms": round(latency, 1),
            "total_memories": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### Acceptance Criteria

- [ ] get_system_health returns all system components
- [ ] Shows Neo4j status and memory count
- [ ] Shows LLM provider status and latency
- [ ] Shows background task schedule
- [ ] Shows system uptime
- [ ] Returns in <2 seconds

---

## Story 5: The Phoenix Cloud Observability

**As a** Brain OS user
**I want** to track all operations in Phoenix Cloud dashboard
**So that** I can see what's happening: tool calls, client inputs, system creations, and responses

### Scenario

```
User opens Phoenix Cloud: https://app.phoenix.arize.com

# Phoenix Dashboard shows:
┌─────────────────────────────────────────────────────────────┐
│ Traces - Last 24 Hours                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 📊 Tool Usage:                                               │
│   create_memory         23 calls  (avg: 145ms)              │
│   get_memory            47 calls  (avg: 89ms)               │
│   get_memory_relations  12 calls  (avg: 3.2s)               │
│   summarize_project     5 calls   (avg: 8.1s)               │
│                                                              │
│ 🔍 Client Input Tracking:                                   │
│   "Remember the meeting about FastTrack project scope"       │
│     → create_memory called                                   │
│     → Sector: Semantic (classified by Groq)                 │
│     → Salience: 0.75                                         │
│                                                              │
│ 💾 System Creations:                                        │
│   Memory ID: 4:abc123... created                            │
│   Node: Bubble(entity="FastTrack", sector="Semantic")       │
│   Stored in Neo4j (45ms write)                               │
│                                                              │
│ 📤 Response Tracking:                                        │
│   "Memory stored: 4:abc123..."                               │
│   Latency: 145ms total                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What Phoenix Tracks

**1. Tool Usage:**
- Which tools are called (create_memory, get_memory, etc.)
- Call frequency and timing
- Success/failure rates
- Error tracking with stack traces

**2. Client Inputs:**
- What data comes from the client (content, sector, query, etc.)
- Input parameters and their values
- Request metadata (timestamps, user context)

**3. System Creations:**
- What memories/data are created in Neo4j
- Memory IDs, sectors, salience scores
- Entity extraction results
- Relationship formations

**4. Responses:**
- What's sent back to the client
- Response times and latency
- Response sizes and formats

**5. LLM Calls:**
- All Groq API calls (classification, extraction)
- All OpenRouter API calls (research, synthesis)
- Prompts and responses
- Token usage and costs

**6. Neo4j Queries:**
- Cypher queries executed
- Query performance
- Result counts

### Technical Implementation

The observability is automatically handled by `src/utils/observability.py`:

```python
# No manual tracking needed - Phoenix automatically traces:
from src.utils.observability import setup_phoenix_tracing

# Setup happens automatically on import
# Just set environment variables:
# PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-username
# PHOENIX_API_KEY=your-api-key-here

# All MCP tool calls are automatically traced with:
# - Tool name and parameters
# - Client input data
# - System operations (Neo4j, LLM calls)
# - Response data and timing
```

### Acceptance Criteria

- [x] Phoenix Cloud dashboard accessible at https://app.phoenix.arize.com
- [x] All tool calls visible in traces
- [x] Client inputs captured (content, sector, query parameters)
- [x] System creations visible (memory IDs, Neo4j operations)
- [x] Responses tracked with latency
- [x] LLM calls visible (Groq + OpenRouter)
- [x] No custom visualization tools needed - Phoenix handles everything

---

## Story 6: The Task Status Query

**As a** Brain OS user
**I want** to check when background tasks will run
**So that** I know when to expect automated maintenance

### Scenario

```
User: "When will the next cloud synthesis run?"

# Phase 4 response:
## Background Task: Cloud Synthesis

Status: Scheduled (healthy)
Schedule: Every 7 days (weekly)
Last Run: 2026-01-07 14:30 UTC
Next Run: 2026-01-14 14:30 UTC (in 5 days)

Last Result:
  Generated 3 Reflective clouds
  Processed 47 memory clusters
  Duration: 2 minutes, 14 seconds

Recent History:
  2026-01-07: Success (3 clouds)
  2026-12-31: Success (2 clouds)
  2026-12-24: Success (4 clouds)
```

### Technical Implementation

```python
# src/tools/monitoring/get_task_status.py
@mcp.tool
async def get_task_status(
    task_name: str = Field(description="Task name or 'all'")
) -> str:
    """Query background task status."""

    if task_name == "all":
        tasks = await get_all_task_status()
    else:
        tasks = [await get_task_status_by_name(task_name)]

    output = ["## Background Task Status\n"]

    for task in tasks:
        output.append(f"### {task['display_name']}")
        output.append(f"**Status**: {task['status']}")
        output.append(f"**Schedule**: Every {task['interval']}")
        output.append(f"**Last Run**: {task['last_run']}")
        output.append(f"**Next Run**: {task['next_run']} ({task['time_until']})")

        if task.get('last_result'):
            output.append(f"\n**Last Result**:")
            output.append(f"  {task['last_result']['summary']}")
            output.append(f"  Duration: {task['last_result']['duration']}")

        if task.get('history'):
            output.append(f"\n**Recent History**:")
            for h in task['history'][-3:]:
                output.append(f"  {h['date']}: {h['status']} ({h['summary']})")

        output.append("")

    return "\n".join(output)
```

### Acceptance Criteria

- [ ] Query single task or all tasks
- [ ] Shows schedule and next run time
- [ ] Shows last run result with duration
- [ ] Shows recent execution history
- [ ] Returns in <500ms

---

## Summary: Phase 4 User Experience

### Before Phase 4
- Black box operations
- No feedback during long operations
- Manual maintenance required
- No visibility into what's happening

### After Phase 4
- **Transparent**: See what Brain OS is doing (Context logs)
- **Responsive**: Progress bars for long operations
- **Self-Maintaining**: Automated pruning and synthesis
- **Observable**: Phoenix Cloud dashboard shows everything
  - Tool calls and timing
  - Client inputs (what comes from user)
  - System creations (what's created in Neo4j)
  - Responses (what's sent back)
  - LLM calls (Groq + OpenRouter)
- **Trustworthy**: Know the system is working

---

**End of Phase 4 User Stories**
