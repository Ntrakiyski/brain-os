# Phase 4: Project Overview

> **Observability, Background Tasks & Circadian Rhythm**
> **Status**: Design Phase | **Complexity**: 2-3 weeks
> **Add-ons Implemented**: Email Notifications + Phoenix Cloud Observability ✅

---

## Quick Summary

Phase 4 transforms Brain OS from a passive memory store into an **active, self-monitoring cognitive system**.

### Three Major Features

1. **Observability & Monitoring** - Client-side logging via FastMCP Context
2. **Background Tasks (Heartbeat)** - Automated maintenance cycles (pruning, synthesis)
3. **Progress Reporting** - Real-time progress for long-running operations

---

## Key Deliverables

### New Tools (2)
- `get_system_health` - Comprehensive system health status
- `get_task_status` - Query background task status

### Background Tasks (3)
- `synaptic_pruning_task` - Daily salience decay for unused memories
- `cloud_synthesis_task` - Weekly generation of Reflective insights
- `health_check_task` - Hourly system health monitoring

### Enhanced Tools (11)
- All existing tools enhanced with Context logging
- Long-running tools (get_memory_relations, summarize_project) enhanced with progress reporting

### Observability via Phoenix Cloud
- **Phoenix Dashboard** - Visual observability for all MCP tool usage
- **Tracking**: Tool calls, client inputs, system creations, responses
- **No custom visual tools needed** - Phoenix provides complete visibility

### ✅ Add-ons Implemented (Phase 4.5)
- **Email Notifications (4 tools)** - N8N webhook integration with 4 templates
- **Phoenix Cloud Observability** - LLM tracing and evaluation dashboard
- **See [final-phase4-addons.md](./final-phase4-addons.md) for details**

---

## Technical Approach

### FastMCP 2.14+ Features

**Context Logging:**
```python
from fastmcp.dependencies import CurrentContext

@mcp.tool
async def create_memory(..., ctx: Context = CurrentContext()):
    await ctx.debug("Starting memory creation")
    await ctx.info(f"Creating {sector} memory")
    # ... work ...
    await ctx.info("Memory stored", extra={"memory_id": id})
```

**Progress Reporting:**
```python
await ctx.report_progress(progress=0, total=100)   # Start
await ctx.report_progress(progress=50, total=100)  # Halfway
await ctx.report_progress(progress=100, total=100) # Complete
```

**Background Tasks:**
```python
@mcp.background_task(interval_hours=24)
async def synaptic_pruning_task():
    """Daily salience decay for unused memories."""
    # ... decay logic ...
```

---

## Implementation Timeline

### Week 1: Logging Foundation
- Add `Context` injection to all 11 existing tools
- Implement structured logging (debug, info, warning, error)
- Test logging output in Claude Desktop

### Week 2: Progress Reporting
- Add progress to `contextual_retrieval` flow
- Add progress to `summarize_project` flow
- Add progress to `instinctive_activation` flow
- Test progress bars in Claude Desktop

### Week 3: Background Tasks
- Implement 3 background tasks (pruning, synthesis, health)
- Create 3 new monitoring tools
- Test background task scheduling
- Documentation and testing

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| **Logging Coverage** | 100% of tools emit Context logs |
| **Progress Visibility** | All flows >2s report progress |
| **Background Tasks** | 3 tasks running automatically |
| **Observability** | All operations tracked in Phoenix Cloud |
| **Performance** | <5% latency overhead from logging |

---

## Detailed Documentation

- **[phase-overview.md](./phase-overview.md)** - Complete technical specification
- **[user-stories.md](./user-stories.md)** - Concrete usage scenarios
- **[api-changes.md](./api-changes.md)** - API changes and new tools
- **[final-phase4-addons.md](./final-phase4-addons.md)** - Email notifications + Phoenix Cloud observability (IMPLEMENTED)

---

## Phase Progression

```
Phase 1: Core MCP + 5 memory tools         ✅ DONE
Phase 2: Modular structure + BaseAgent     ✅ DONE
Phase 3: Instinctive memory + Contextual   ✅ DONE
Phase 4: Observability + Background Tasks  🔄 NEXT
```

---

## Questions Before Approval

1. **Background task storage**: Should task status be stored in Neo4j or in-memory?
   - **Recommendation**: Neo4j with `TaskStatus` nodes for persistence

2. **Synaptic pruning rate**: How aggressive should salience decay be?
   - **Recommendation**: 10% decay per month for memories inactive 30+ days

3. **Cloud synthesis threshold**: When to auto-generate insights?
   - **Recommendation**: Clusters with 5+ memories >0.7 salience

---

**Ready for implementation upon approval.**
