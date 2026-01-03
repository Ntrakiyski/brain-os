# FastMCP Features Reference

> **Purpose:** Reference guide for FastMCP capabilities beyond Tools - Resources, Prompts, and Context features.

FastMCP supports **4 main resource types** for building MCP servers. Brain OS currently uses **Tools**, but this document explains all available features for future development.

---

## 1. Tools (`@mcp.tool`)

**Purpose:** Functions that LLMs can execute with side effects (like POST requests).

**Current Usage in Brain OS:**
- `create_memory` - Store new memories
- `get_memory` - Search memories by query
- `get_all_memories` - Retrieve all memories
- `visualize_memories` - Generate memory charts
- `list_sectors` - List cognitive sectors

**Pattern:**
```python
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Brain OS")

@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    sector: str = Field(description="Cognitive sector"),
    salience: float = Field(default=0.5, ge=0.0, le=1.0),
) -> str:
    """Store a new memory in the Synaptic Graph."""
    # Implementation with side effects
    return "Memory stored successfully"
```

**When to Use:**
- Actions that modify state
- Database operations (create, update, delete)
- API calls with side effects
- Computations that need to return results

---

## 2. Resources (`@mcp.resource`)

**Purpose:** Read-only data sources that the LLM can access (like GET endpoints).

**Key Characteristics:**
- No side effects (idempotent)
- Can be static or dynamic (with templates)
- Accessed via URI patterns
- Useful for exposing system state

### Static Resource

```python
@mcp.resource("config://version")
def get_version() -> str:
    """Return the current Brain OS version."""
    return "2.0.1"
```

### Dynamic Template Resource

```python
@mcp.resource("brainos://sector/{sector_name}/stats")
def get_sector_stats(sector_name: str) -> str:
    """Get statistics for a specific cognitive sector."""
    stats = calculate_sector_stats(sector_name)
    return json.dumps({
        "sector": sector_name,
        "count": stats["count"],
        "avg_salience": stats["avg_salience"]
    })
```

### Resource for Brain OS (Potential Future Use)

```python
@mcp.resource("brainos://stats")
def brain_stats() -> str:
    """Quick access to memory statistics."""
    total, by_sector = get_memory_counts()
    return json.dumps({
        "total_memories": total,
        "sector_distribution": by_sector,
        "last_updated": datetime.now(timezone.utc).isoformat()
    })

@mcp.resource("brainos://recent/{limit}")
def recent_memories(limit: int = 10) -> str:
    """Get recent memories as a resource."""
    bubbles = await get_all_bubbles(limit)
    return json.dumps([b.model_dump() for b in bubbles])

@mcp.resource("brainos://export")
def export_all_memories() -> str:
    """Export all memories as JSON."""
    bubbles = await get_all_bubbles(limit=1000)
    return json.dumps({
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total": len(bubbles),
        "memories": [b.model_dump() for b in bubbles]
    })
```

**When to Use:**
- Exposing configuration or system state
- Providing data for LLM to read without calling a tool
- Static or semi-static content
- Cross-referencing between different data sources

**Access Pattern:**
LLM says "read brainos://stats" instead of "call get_stats tool"

---

## 3. Prompts (`@mcp.prompt`)

**Purpose:** Reusable message templates that the LLM can use.

**Key Characteristics:**
- Pre-built prompt templates
- Can accept parameters
- Return strings or Message objects
- Useful for common interaction patterns

### Simple Prompt (Returns String)

```python
@mcp.prompt
def weekly_synthesis() -> str:
    """Generate a weekly memory synthesis prompt."""
    return """Analyze all memories from the past week and identify:
1. Key themes across sectors
2. Unexpected connections between disparate memories
3. Areas needing more attention or data collection

Please provide a structured summary with actionable insights."""
```

### Parameterized Prompt

```python
@mcp.prompt
def sector_analysis(sector: str) -> str:
    """Analyze memories in a specific cognitive sector."""
    return f"""Review all {sector} memories and provide insights about:

1. Dominant patterns and themes
2. Salience trends over time
3. Gaps in knowledge or understanding
4. Connections to other sectors

Focus on actionable insights for improving the {sector} knowledge base."""
```

### Advanced Prompt (Returns Message Objects)

```python
from fastmcp import Message

@mcp.prompt
def synthesis_prompt(memory_ids: list[str]) -> list[Message]:
    """Create a synthesis prompt for specific memories."""
    return [
        Message(
            role="system",
            content="You are a cognitive synthesizer specializing in memory integration."
        ),
        Message(
            role="user",
            content=f"""Synthesize these memories into coherent insights:
{format_memories(memory_ids)}

Focus on:
- Cross-sector connections
- Emerging patterns
- Actionable conclusions"""
        )
    ]
```

### Brain OS Prompt Examples (Potential Future Use)

```python
@mcp.prompt
def daily_review() -> str:
    """Daily memory review prompt template."""
    return """Review today's memories and:
1. Highlight the most salient (important) items
2. Identify any themes across sectors
3. Suggest connections to store for future reference
4. Flag anything needing follow-up tomorrow"""

@mcp.prompt
def sector_deep_dive(sector: str, days: int = 7) -> str:
    """Deep dive into a specific sector's recent memories."""
    return f"""Analyze all {sector} memories from the past {days} days:

1. What patterns emerge?
2. What's missing or underrepresented?
3. How does salience correlate with importance?
4. What connections exist to other sectors?

Provide specific examples and actionable insights."""

@mcp.prompt
def connection_finder(min_salience: float = 0.7) -> str:
    """Find potential connections between high-salience memories."""
    return f"""Review all memories with salience >= {min_salience} and identify:
1. Unexpected relationships or themes
2. Temporal patterns (events that cluster in time)
3. Cross-sector references
4. Opportunities to create new "Cloud" insights"""
```

**When to Use:**
- Common interaction patterns (daily review, weekly synthesis)
- Complex prompts used repeatedly
- Guided analysis workflows
- When you want the LLM to "use a template" instead of you explaining

**Access Pattern:**
LLM says "use the daily_review prompt" instead of you typing the instructions

---

## 4. Context Features (`ctx: Context`)

**Purpose:** Access MCP session capabilities within tools, resources, or prompts.

**Key Feature:** Add a `ctx: Context` parameter to any `@mcp` decorated function:

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("Brain OS")

@mcp.tool
async def process_data(data: str, ctx: Context) -> str:
    # Use context features
    await ctx.info("Starting processing...")
    await ctx.progress(0, 100)

    # Do work...
    await ctx.progress(50, 100)

    return "Processing complete"
```

### Available Context Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| `ctx.info(message)` | Send info log to client | Progress updates, status messages |
| `ctx.warning(message)` | Send warning log | Non-critical issues |
| `ctx.error(message)` | Send error log | Error conditions |
| `ctx.debug(message)` | Send debug log | Troubleshooting |
| `ctx.progress(current, total)` | Report progress | Long-running operations |
| `ctx.read_resource(uri)` | Read a resource from this server | Cross-resource composition |
| `ctx.sample(messages)` | Request LLM completion | Ask client's LLM to process data |

### Progress Reporting Example

```python
@mcp.tool
async def import_transcript(file_path: str, ctx: Context) -> str:
    """Import a transcript and create multiple memories."""
    await ctx.info(f"Starting import from {file_path}")

    transcript = await read_transcript(file_path)
    total_chunks = len(transcript.chunks)

    memories_created = 0
    for i, chunk in enumerate(transcript.chunks):
        # Process chunk
        await create_memory(chunk.content, chunk.sector)
        memories_created += 1

        # Report progress
        await ctx.progress(i + 1, total_chunks)
        await ctx.info(f"Processed {i + 1}/{total_chunks} chunks")

    await ctx.info(f"Import complete: {memories_created} memories created")
    return f"Successfully imported {memories_created} memories"
```

### LLM Sampling Example

```python
@mcp.tool
async def synthesize_insight(ctx: Context) -> str:
    """Use the client's LLM to synthesize an insight."""
    await ctx.info("Gathering memories for synthesis...")

    # Get recent memories
    memories = await get_all_bubbles(limit=20)
    memory_text = format_memories(memories)

    await ctx.info("Requesting synthesis from LLM...")

    # Ask the client's LLM to synthesize
    result = await ctx.sample(f"""
    Analyze these memories and create a cohesive insight:

    {memory_text}

    Provide: 1) Key theme, 2) Supporting evidence, 3) Actionable conclusion
    """)

    await ctx.info("Insight synthesized successfully")

    # Store the synthesized insight as a new memory
    insight = await create_memory(
        content=result.text,
        sector="Reflective",
        source="llm_synthesis",
        salience=0.8
    )

    return f"Created insight: {insight.id}"
```

### Resource Access Example

```python
@mcp.tool
async def analyze_with_config(ctx: Context) -> str:
    """Analyze memories using configuration from a resource."""
    # Read configuration from a resource
    config = await ctx.read_resource("config://analysis")
    settings = json.loads(config.content[0].text)

    # Use settings to guide analysis
    memories = await get_all_bubbles(limit=settings["max_memories"])

    return f"Analyzed {len(memories)} memories using {settings}"
```

**When to Use:**
- Long-running operations (progress reporting)
- Need to read other resources from your own server
- Want the client's LLM to process data
- Debugging or logging to client

---

## Decision Matrix: When to Use What?

| Scenario | Use This | Example |
|----------|----------|---------|
| Modify database state | **Tool** | `create_memory`, `delete_memory` |
| Read-only system state | **Resource** | `brainos://stats`, `config://version` |
| Reusable prompt template | **Prompt** | `daily_review`, `weekly_synthesis` |
| Long-running operation | **Tool + Context** | Import with progress updates |
| Cross-resource composition | **Tool + Context** | Read config + process data |
| Client-side LLM processing | **Tool + Context** | Ask LLM to synthesize insights |

---

## Quick Reference

### Decorators

```python
@mcp.tool                    # Executable function with side effects
@mcp.resource("uri://path")  # Read-only data source
@mcp.prompt                   # Reusable message template
```

### Context Parameter

```python
async def my_function(ctx: Context):
    await ctx.info(message)        # Log info
    await ctx.progress(curr, total) # Progress
    await ctx.read_resource(uri)    # Read resource
    result = await ctx.sample(msg)  # LLM completion
```

### URI Patterns for Resources

```python
"config://version"              # Static config
"brainos://stats"               # Dynamic stats
"brainos://sector/{name}/stats" # Template with parameters
"brainos://recent/{limit}"      # Template with parameters
```

---

## Brain OS Status

| Feature | Status | Examples |
|---------|--------|----------|
| **Tools** | ✅ Implemented | `create_memory`, `get_memory`, `get_all_memories`, `visualize_memories`, `list_sectors` |
| **Resources** | ❌ Not implemented | Could add: `brainos://stats`, `brainos://export`, `config://version` |
| **Prompts** | ❌ Not implemented | Could add: `daily_review`, `weekly_synthesis`, `sector_deep_dive` |
| **Context** | ❌ Not implemented | Could add: Progress for imports, LLM sampling for synthesis |

---

## Further Reading

- [FastMCP Documentation](https://gofastmcp.com)
- [FastMCP Server Reference](https://gofastmcp.com/servers/server.md)
- [Resources & Templates](https://gofastmcp.com/servers/resources.md)
- [Prompts](https://gofastmcp.com/servers/prompts.md)
- [MCP Context](https://gofastmcp.com/servers/context.md)
