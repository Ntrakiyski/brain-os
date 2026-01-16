# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**0brainOS** is a cognitive operating system designed as a symbiotic AI-human system. The human provides strategic direction ("The Brand") while the OS handles "metabolic thinking" (technical implementation, routine analysis, memory management).

### Core Philosophy
- **Bubbles and Clouds**: Raw episodic memories (Bubbles) and AI-generated insights (Clouds)
- **Five-Sector Ontology**: Episodic, Semantic, Procedural, Emotional, Reflective
- **Neurochain Architecture**: Single-waypoint connections with synaptic weights
- **Salience Scoring**: Adaptive memory with decay and reinforcement (0.0 to 1.0)

### Technical Stack
- **Runtime**: Python 3.12+ with `uv` package manager (Phoenix requires <3.14)
- **MCP Framework**: FastMCP 2.x for tools, background tasks, and remote proxy mounting
- **Agent Framework**: PocketFlow (100-line minimalist framework) for workflow orchestration
- **Database**: Neo4j Community Edition for the Synaptic Graph
- **Observability**: Phoenix Cloud (Arize) for real-time tracing and monitoring
- **Intelligence**: Dual-LLM architecture
  - **Groq**: Fast actions (classification, extraction, routing) - speed and cost efficiency
  - **OpenRouter**: Deep thinking (research, synthesis, complex reasoning) - quality and intelligence

## Development Commands

### Setup
```bash
# Add dependencies
uv add fastmcp pocketflow neo4j python-dotenv pydantic groq openai arize-phoenix-otel httpx

# Verify FastMCP installation
fastmcp version
```

### Running Servers
```bash
# Start Neo4j Docker container (required first)
docker compose up -d

# Neo4j Browser available at: http://localhost:7474
# Default credentials: neo4j / brainos_password_123

# Run main MCP server with stdio (FastMCP CLI)
fastmcp run brainos_server.py:mcp

# Run with HTTP transport directly via Python (recommended for Coolify/HTTPS)
python brainos_server.py
# Or with custom port:
MCP_PORT=8000 python brainos_server.py

# Run with Docker
docker compose up --build
```

### Docker Deployment

The project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment:

**Local Docker:**
```bash
docker compose up --build
# Note: Ports are exposed internally only (not published to host)
# For local testing, temporarily change 'expose' to 'ports' in docker-compose.yml
```

**Production Notes (Coolify/HTTPS):**
- Port: **9131** (internal container port - Coolify proxy connects here)
- Port exposure: Uses `expose` (internal only) - Coolify handles external HTTPS routing
- Transport: Streamable HTTP with HTTPS termination at Coolify's reverse proxy
- Authentication: None (run open - add proxy auth for production)
- Pattern: Matches chrome-mcp deployment pattern (proven to work with Coolify HTTPS)
- **Neo4j: Deployed separately** - See "Neo4j Deployment Guide" below

### Neo4j Deployment Guide

**BrainOS now connects to an external Neo4j instance** to avoid Coolify environment variable conflicts.

**Deployment Options:**

1. **Coolify Deployment (Recommended):**
   - Deploy Neo4j as a separate service in Coolify
   - Use internal service URL: `bolt://neo4j-service-name:7687`
   - Set `NEO4J_URI` in BrainOS environment to point to this service
   - See separate Neo4j deployment repo for full setup

2. **Cloud Neo4j (Neo4j Aura):**
   - Free tier available at https://neo4j.com/cloud/aura/
   - Get connection URI like `neo4j+s://xxxxx.databases.neo4j.io`
   - Set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` in BrainOS

3. **Local Development:**
   - Run Neo4j locally: `docker run -p 7687:7687 -p 7474:7474 neo4j:5.25-community`
   - Use `NEO4J_URI=bolt://localhost:7687`

**Important:** All your schema, queries, and data structure are defined in BrainOS code (`src/database/`), not in Neo4j deployment.

### Claude Desktop Integration (Local Development)

**Recommended: Use FastMCP CLI installer**

The easiest way to integrate Brain OS with Claude Desktop is using the FastMCP CLI:

```bash
# From your project directory
fastmcp install claude-desktop brainos_server.py --project . --env-file .env
```

This automatically:
- Configures the correct absolute paths
- Sets up the project directory for dependency discovery
- Loads environment variables from `.env`
- Handles all STDIO transport configuration

After running the command, **restart Claude Desktop completely** and look for the hammer icon (🔨) to confirm the server loaded.

**Manual Configuration**

If you prefer manual configuration, edit your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "brain-os": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "C:\\Users\\nikol\\Desktop\\new-apps\\0brainOS",
        "fastmcp",
        "run",
        "C:\\Users\\nikol\\Desktop\\new-apps\\0brainOS\\brainos_server.py:mcp"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password",
        "GROQ_API_KEY": "your-key",
        "OPENROUTER_API_KEY": "your-key"
      }
    }
  }
}
```

**Important Notes:**
- Use **absolute paths** - Claude Desktop resolves relative paths from its own installation directory
- Always restart Claude Desktop after config changes
- Ensure Neo4j is running before starting Claude Desktop
- All environment variables must be explicitly passed (Claude Desktop has no shell access)

### Environment Variables Required
```env
# Neo4j (external instance - deploy separately in Coolify)
# For Coolify: Use internal service URL like bolt://neo4j-service:7687
# For local dev: Use bolt://localhost:7687
NEO4J_URI=bolt://your-neo4j-host:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password

# Groq (fast actions)
GROQ_API_KEY=<your-groq-key>
GROQ_QUICK_MODEL=openai/gpt-oss-120b

# OpenRouter (deep thinking)
OPENROUTER_API_KEY=<your-openrouter-key>
OPENROUTER_RESEARCHING_MODEL=anthropic/claude-sonnet-4
OPENROUTER_THINKINIG_MODEL=anthropic/claude-sonnet-4
OPENROUTER_CREATIVE_MODEL=anthropic/claude-sonnet-4
OPENROUTER_PLANNING_MODEL=anthropic/claude-opus-4

# Phoenix Cloud Observability (OPTIONAL)
# Get free account at: https://phoenix.arize.com/
# Benefits: Real-time tracing, performance monitoring, interactive debugging
# Format: Your Phoenix Cloud project URL (e.g., https://app.phoenix.arize.com/s/your-space-id)
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-space-id
PHOENIX_API_KEY=<your-phoenix-api-key>

# MCP Server (optional)
MCP_PORT=9131
```

**Important Notes:**
- **Neo4j is now deployed separately** - See "Neo4j Deployment" section below
- Do NOT commit `.env` or `.env.example` files
- In Coolify, set all environment variables in the UI, not in files

## Architecture Overview

### Fractal DNA: Modular Hierarchy (Maps to PocketFlow)
- **Cells** → `AsyncNode.exec()`: Atomic utility functions (LLM calls, schema validators)
- **Organs** → `AsyncFlow`: Specialized agent clusters (Researcher, Technical Auditor, Synthesizer)
- **Organisms** → Nested `AsyncFlow`: Multi-agent workflows (Ingestion, Weekly Synthesis)

### Project Structure (Phase 3 - Design Complete)
```
0brainos/
├── src/
│   ├── core/
│   │   └── config.py          # Frozen dataclasses for configuration
│   ├── database/
│   │   ├── connection.py      # Neo4j async driver with global connection singleton
│   │   └── queries/           # Modular query organization
│   │       ├── __init__.py
│   │       ├── memory.py      # Bubble CRUD operations
│   │       └── relations.py   # Relationship queries (Phase 3)
│   ├── flows/                 # PocketFlow workflows (replaces src/agents/)
│   │   ├── __init__.py
│   │   ├── instinctive_activation.py    # Instinctive memory activation flow
│   │   ├── contextual_retrieval.py      # Pre/post-query contextual retrieval
│   │   ├── entity_extraction.py         # Entity extraction from bubbles
│   │   └── summarize_project.py         # Project summary flow (migrated)
│   ├── tools/                 # MCP tool wrappers
│   │   ├── __init__.py
│   │   ├── memory/            # Memory-related tools
│   │   │   ├── __init__.py
│   │   │   ├── create_memory.py         # create_memory (enhanced Phase 3)
│   │   │   ├── get_memory.py            # get_memory, get_all_memories
│   │   │   ├── list_sectors.py          # list_sectors
│   │   │   ├── visualize_memories.py    # visualize_memories
│   │   │   ├── instinctive_memory.py    # get_instinctive_memory (Phase 3)
│   │   │   ├── get_relations.py         # get_memory_relations (Phase 3)
│   │   │   └── visualize_relations.py   # visualize_relations (Phase 3)
│   │   └── agents/            # Flow-based tool wrappers
│   │       ├── __init__.py
│   │       └── summarize_project.py     # summarize_project (uses PocketFlow)
│   └── utils/
│       ├── schemas.py         # Pydantic validation models
│       └── llm.py             # LLM client factory (Groq, OpenRouter)
├── brainos_server.py          # ROOT-level MCP server entry point (FastMCP)
├── Dockerfile                 # Container image with HTTP transport on port 9131
├── docker-compose.yml         # Multi-service: brainos + neo4j
├── pyproject.toml             # Dependencies (fastmcp, pocketflow, neo4j, groq, pydantic)
├── CLAUDE.md                  # This file - project documentation
├── docs/
│   ├── project/
│   │   ├── inspiration.md     # Project inspiration (Pickle OS concept)
│   │   ├── full_project_idea.md # Master specification
│   │   ├── neo4j_memory.md    # Neo4j implementation notes
│   │   ├── phase1/            # Phase 1 documentation
│   │   ├── phase2/            # Phase 2 documentation
│   │   └── phase3/            # Phase 3 documentation (design complete)
│   └── libraries/             # External library documentation
└── fastmcp_demo_app/          # FastMCP learning examples
```

**Architecture Change (Phase 3)**: `src/agents/` replaced by `src/flows/` using PocketFlow AsyncNode/AsyncFlow patterns.

### Key Concepts

**Memory Retrieval Scoring**: Composite formula with 60% similarity, 20% salience, 10% recency, 10% connection strength.

**Remote Proxy Mounting**: FastMCP can dynamically mount external MCP servers (Gmail, Calendar) via SSE/HTTP without code restart.

**Validity Windows**: Track temporal evolution with `valid_from` and `valid_to` timestamps for audit trails.

## Current Status

**🎉 ALL PHASES COMPLETE (Phase 1-4)**

Brain OS is now a fully functional cognitive operating system with observability, maintenance, and health monitoring.

### Phase 1: ✅ COMPLETED
Phase 1 successfully established the foundational infrastructure:
- ✅ MCP server with 5 tools (`create_memory`, `get_memory`, `get_all_memories`, `list_sectors`, `visualize_memories`)
- ✅ Neo4j integration with async connection pooling
- ✅ Claude Desktop integration via FastMCP CLI
- ✅ Configuration management with frozen dataclasses
- ✅ Pydantic validation for all data operations
- ✅ Memory visualization with sector distribution charts
- ✅ Docker deployment with docker-compose
- ✅ HTTP transport on port 9131 with stateless mode
- ✅ Health check endpoint at `/health`

### Phase 2: ✅ COMPLETED
Phase 2 established the scalable foundation for 20+ agents and 70+ tools:
- ✅ Modular folder structure (tools organized by function in separate files)
- ✅ BaseAgent pattern with configuration-driven execution
- ✅ LLM utility with Groq + OpenRouter client factories
- ✅ First agent built: `summarize_project` (AI-powered project summaries)
- ✅ 3-step pattern for adding new agents without code changes
- ✅ PocketFlow installed (available for future workflow orchestration)
- ✅ brainos_server.py simplified from 154 to 65 lines

**New Tool Added:**
- `summarize_project`: Retrieves project memories and generates AI summaries using OpenRouter

**Key Design Principle:** To change agent behavior, modify `AgentConfig`. Never touch the agent code.

### Phase 3: ✅ COMPLETED
Phase 3 transforms Brain OS into a cognitive operating system with instinctive memory and contextual retrieval:
- ✅ **Implementation Complete**: All Phase 3 features fully implemented and tested
- ✅ **Testing**: 11/11 tools passed (100% success rate)
- ✅ **Key Features Implemented**:
  - **Instinctive Memory System**: Auto-activation without conscious search (the "Oven Analogy")
  - **Contextual Retrieval**: 3-agent system (pre-query → Neo4j → post-query synthesis)
  - **Entity-Observation Model**: Enhanced bubble schema with entities and observations
  - **Relationship Visualization**: Mermaid diagrams + Neo4j Browser queries
  - **Server-Level Instructions**: 90+ lines of comprehensive guidance for Claude
  - **Resources System**: 4 static documentation resources for LLM consumption
  - **Prompt Templates**: 4 reusable workflow prompts
  - **Deletion Tools**: Safe memory deletion with confirmation requirements
- ✅ **Architecture Migration**: Replaced BaseAgent with PocketFlow AsyncNode/AsyncFlow
- ✅ **New Tools**:
  - `get_instinctive_memory`: Automatic memory activation based on context
  - `get_memory_relations`: Deep retrieval with contextual understanding
  - `visualize_relations`: Interactive relationship visualization
  - `delete_memory`: Delete specific memory with safety confirmation
  - `delete_all_memories`: Mass deletion with "DELETE_ALL" confirmation

**Documentation:**
- See `docs/COMPLETE_USER_GUIDE.md` for comprehensive user guide
- See `docs/project/phase3/` for design specifications

### Phase 4: ✅ COMPLETED
Phase 4 adds observability, maintenance, and health monitoring:
- ✅ **Enhanced Logging**: All tools and PocketFlow nodes emit debug/info/warning/error logs
- ✅ **Progress Reporting**: Long-running operations (summarize_project) report progress at key stages
- ✅ **Background Tasks**: Circadian rhythm maintenance cycles
  - **Synaptic Pruning** (daily, 24h): Decays salience of memories not accessed in 30+ days
  - **Cloud Synthesis** (weekly, 168h): Generates Reflective insights from memory clusters
  - **Health Check** (hourly, 1h): Monitors Neo4j and LLM API availability
- ✅ **System Health Check**: `get_system_health` tool for comprehensive system status
- ✅ **Task Status Query**: `get_task_status` tool for background task monitoring
- ✅ **Phoenix Cloud Integration**: Visual observability dashboard for all operations

**New Tools Added:**
- `get_system_health`: Neo4j connectivity, memory statistics, LLM provider status
- `get_task_status`: Query background task status and schedule

**New Modules:**
- `src/tasks/background.py`: Background task implementations
- `src/tools/monitoring/`: System health and monitoring tools

**Documentation:**
- See `docs/IMPLEMENTATION_SUMMARY.md` for complete implementation overview

### HTTP Deployment Notes:
- **Local**: Works perfectly - `http://localhost:9131/mcp`
- **Docker Compose**: Works locally with both services (brainos + neo4j)
- **Coolify/Cloud**: **Now supports HTTPS** - Server runs directly via `mcp.run()` for proxy compatibility
  - MCP protocol uses `text/event-stream` content-type
  - Coolify terminates HTTPS and forwards to container as HTTP
  - Server is configured for proxy-friendly operation (direct Python mode, not CLI)
  - Based on chrome-mcp pattern proven to work with Coolify HTTPS

See `docs/project/phase1/` for Phase 1 documentation, `docs/project/phase2/` for Phase 2 documentation, and `docs/project/full_project_idea.md` for the master specification.

## FastMCP Patterns

Define tools using the `@mcp.tool` decorator on async functions with Pydantic Fields for LLM-friendly descriptions:
```python
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Brain OS")

@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    sector: str = Field(description="Cognitive sector: Episodic, Semantic, Procedural, Emotional, or Reflective"),
    source: str = Field(default="direct_chat", description="Origin of the data"),
    salience: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score from 0.0 to 1.0"),
) -> str:
    """Store a new memory in the Synaptic Graph."""
    # Implementation: validate -> upsert to Neo4j -> return result
    return f"Memory stored with ID: {result.id}"
```

**Key Patterns:**
- Use `Field()` descriptions to help LLMs understand parameters
- Use `ge`/`le` constraints for numeric validation
- Provide sensible defaults for optional parameters
- Return user-friendly formatted strings, not raw data

**Version Pinning**: Use `fastmcp>=2.14.2` to allow patch updates while avoiding breaking changes.

## FastMCP Meta-Communication Features

Beyond tools, FastMCP provides powerful features for giving instructions and best practices to LLM interfaces.

### Server-Level Instructions (`FastMCP(instructions=...)`)

The MCP server includes 90+ lines of comprehensive guidance that Claude sees when connecting:

```python
mcp = FastMCP(
    "Brain OS",
    instructions="""
    You are interacting with Brain OS, a cognitive operating system...

    ## THE OVEN ANALOGY
    Instinctive memory auto-activates like a hot oven reminds you of food...

    ## TOOL SELECTION GUIDE
    - get_memory: Quick keyword search
    - get_instinctive_memory: Context switching
    - get_memory_relations: Deep contextual queries

    ## BEST PRACTICES
    - Include WHY in content, not just WHAT
    - Use consistent entity names
    - Set appropriate salience
    """
)
```

**What this provides:**
- Global guidance for all tool interactions
- Tool selection recommendations
- Best practices for memory creation
- Cognitive balance indicators
- Common workflow patterns

### Resources (`@mcp.resource`)

Static documentation that LLMs can read via `brainos://` URIs:

| Resource | Purpose | Usage |
|----------|---------|-------|
| `brainos://guide` | Complete user guide | "Read the brainos://guide resource" |
| `brainos://philosophy` | Core philosophy concepts | "Read brainos://philosophy" |
| `brainos://tool-reference` | Quick tool reference | "Read brainos://tool-reference" |
| `brainos://prompts` | Prompt templates guide | "Read brainos://prompts" |

**How to use:**
```python
@mcp.resource("brainos://guide")
async def user_guide_resource() -> str:
    """Complete user guide for Brain OS best practices."""
    guide_path = project_root / "docs" / "COMPLETE_USER_GUIDE.md"
    return guide_path.read_text() if guide_path.exists() else "Not found"
```

### Prompts (`@mcp.prompt`)

Reusable prompt templates for common workflows:

| Prompt | Purpose | Usage |
|--------|---------|-------|
| `weekly_review` | End-of-week cognitive review | "Use the weekly_review prompt" |
| `project_start` | Load context when starting work | "Use project_start for Project A" |
| `decision_support` | Decision-making with past experience | "Use decision_support prompt" |
| `cognitive_balance` | Check and rebalance cognitive state | "Use cognitive_balance prompt" |

**How to use:**
```python
@mcp.prompt("weekly_review")
async def weekly_review_prompt() -> str:
    """Generate a structured weekly review of all memories."""
    return """
    Please help me with a weekly review...
    1. Run get_all_memories(limit=100)
    2. Run list_sectors()
    3. Create Reflective summary
    """
```

**Note:** Prompts may not be visible in all MCP clients. Reference them by name in conversation.

### Enhanced Tool Descriptions

All tools now have comprehensive Field descriptions and docstrings:

```python
@mcp.tool
async def create_memory(
    content: str = Field(
        description="What to remember. Include WHY, not just WHAT"
    ),
    sector: str = Field(
        description="Cognitive sector. REQUIRED - Choose from: Episodic, Semantic, Procedural, Emotional, Reflective"
    ),
    salience: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance: 0.9-1.0 (business-critical), 0.7-0.8 (important), 0.5-0.6 (routine)"
    ),
) -> str:
    """
    Store a new memory in the Synaptic Graph.

    **Use this for ANY information worth remembering.**

    Best Practices:
    - Include decision rationale in observations
    - Use consistent entity names
    - Set appropriate salience

    Common Patterns:
    **Decision**: Semantic + instinctive + high salience
    **Meeting**: Episodic + thinking + medium salience
    """
```

### Deletion Tools with Safety

Two deletion tools with confirmation requirements:

**`delete_memory`**: Delete specific memory
- Requires `confirm=True` to prevent accidental deletion
- Shows what will be deleted before deleting
- Uses soft deletion (sets `valid_to` timestamp)

**`delete_all_memories`**: Delete ALL memories
- Requires `confirm="DELETE_ALL"` (exact string match)
- Shows count before deletion
- Warns about data loss
- Suggests alternatives

## PocketFlow Pattern (Phase 3)

Brain OS uses **PocketFlow AsyncNode/AsyncFlow** patterns for workflow orchestration:
- **Flow Layer** (`src/flows/`): PocketFlow workflows with AsyncNode implementations
- **Tool Layer** (`src/tools/`): MCP tool wrappers that expose flows to Claude

### Creating a New Flow (3-Step Pattern)

**Step 1: Define the AsyncNode Flow**
```python
# src/flows/my_flow.py
from pocketflow import AsyncNode, AsyncFlow

class MyProcessNode(AsyncNode):
    """AsyncNode for processing input."""

    async def prep_async(self, shared):
        # Extract from shared store
        return shared["input"]

    async def exec_async(self, inputs):
        # Execute core logic (LLM call, DB query, etc.)
        return await process_logic(inputs)

    async def post_async(self, shared, prep_res, exec_res):
        # Write to shared store, return action
        shared["output"] = exec_res
        return "default"

# Wire the flow
my_node = MyProcessNode()
my_flow = AsyncFlow(start=my_node)
```

**Step 2: Create MCP Tool Wrapper**
```python
# src/tools/my_tool.py
from pydantic import Field
from src.flows.my_flow import my_flow

def register_my_tool(mcp) -> None:
    @mcp.tool
    async def my_tool(
        input: str = Field(description="Input to process")
    ) -> str:
        """Process input using PocketFlow workflow."""
        from src.database.connection import get_driver

        # Prepare shared store
        shared = {
            "neo4j_driver": get_driver(),
            "input": input
        }

        # Run the flow
        await my_flow.run_async(shared)

        # Return result
        return shared.get("output", "No output generated")
```

**Step 3: Register the Tool**
```python
# src/tools/__init__.py
from src.tools.my_tool import register_my_tool

def register_all_tools(mcp) -> None:
    register_my_tool(mcp)  # Add this line
```

### PocketFlow Node Lifecycle

Each AsyncNode has three async methods:
- `prep_async(shared)`: Read/prepare from shared store → returns prep_res
- `exec_async(prep_res)`: Execute core logic (LLM, DB) → returns exec_res
- `post_async(shared, prep_res, exec_res)`: Write to shared, return action

### Flow Chaining Patterns

```python
# Sequential flow
node1 >> node2 >> node3

# Conditional flow
node1 - "action_name" >> node2

# Mixed flow
node1 >> (node2 - "special" >> node3) >> node4
```

### LLM Utility

Use `src/utils/llm.py` for direct LLM access:

```python
from src.utils.llm import get_groq_client, get_openrouter_client

# Fast actions (~100ms)
groq = get_groq_client()

# Deep thinking (~3-10s)
openrouter = await get_openrouter_client()
```

## Dual-LLM Strategy

Brain OS uses two LLM providers for different purposes:

### Groq (System 1 - Fast Actions)
Use Groq for quick, deterministic tasks:
- Sector classification (Episodic/Semantic/Procedural/Emotional/Reflective)
- Entity extraction (names, dates, locations)
- Sentiment analysis
- Data formatting and validation
- Routing decisions in workflows

```python
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_sector(text: str) -> str:
    """Quick classification using Groq."""
    response = client.chat.completions.create(
        model=os.getenv("GROQ_QUICK_MODEL"),
        messages=[
            {"role": "system", "content": "Classify text into one of: Episodic, Semantic, Procedural, Emotional, Reflective"},
            {"role": "user", "content": text}
        ],
        temperature=0,
        max_tokens=10,
        stream=False
    )
    return response.choices[0].message.content.strip()
```

### OpenRouter (System 2 - Deep Thinking)
Use OpenRouter for cognitively demanding tasks:
- **Researching**: Information gathering and analysis (uses `OPENROUTER_RESEARCHING_MODEL`)
- **Thinking**: Complex reasoning and validation (uses `OPENROUTER_THINKINIG_MODEL`)
- **Creative**: Cloud generation and synthesis (uses `OPENROUTER_CREATIVE_MODEL`)
- **Planning**: Multi-step strategic planning (uses `OPENROUTER_PLANNING_MODEL`)

```python
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

async def synthesize_cloud(memories: list) -> str:
    """Deep synthesis using OpenRouter CREATIVE model."""
    response = await client.chat.completions.create(
        model=os.getenv("OPENROUTER_CREATIVE_MODEL"),
        messages=[
            {"role": "system", "content": "Synthesize these memories into a coherent insight..."},
            {"role": "user", "content": format_memories(memories)}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content

async def research_topic(query: str) -> str:
    """Research using OpenRouter RESEARCHING model."""
    response = await client.chat.completions.create(
        model=os.getenv("OPENROUTER_RESEARCHING_MODEL"),
        messages=[
            {"role": "system", "content": "You are a research assistant..."},
            {"role": "user", "content": query}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    return response.choices[0].message.content
```

**Decision Matrix:**
| Task Type | Use | Model Env Var | Speed | Cost | Quality |
|-----------|-----|---------------|-------|------|---------|
| Classification | Groq | GROQ_QUICK_MODEL | ~100ms | Low | Good enough |
| Extraction | Groq | GROQ_QUICK_MODEL | ~200ms | Low | Good enough |
| Routing | Groq | GROQ_QUICK_MODEL | ~100ms | Low | Good enough |
| Research | OpenRouter | OPENROUTER_RESEARCHING_MODEL | ~2-5s | Medium | Excellent |
| Reasoning | OpenRouter | OPENROUTER_THINKINIG_MODEL | ~3-8s | Medium | Excellent |
| Synthesis | OpenRouter | OPENROUTER_CREATIVE_MODEL | ~3-10s | Medium | Excellent |
| Planning | OpenRouter | OPENROUTER_PLANNING_MODEL | ~5-15s | High | Excellent |

## PocketFlow Patterns

PocketFlow provides a 100-line framework for orchestrating async workflows. The core abstraction is `AsyncNode`:

```python
from pocketflow import AsyncNode, AsyncFlow
from fastmcp import Client

# Define a Cell (atomic operation)
class CreateMemoryNode(AsyncNode):
    async def exec_async(self, prep_res):
        content, sector = prep_res
        async with Client("http://localhost:8000/mcp") as brain:
            result = await brain.call_tool("create_memory", {
                "content": content,
                "sector": sector,
                "source": "agent"
            })
        return result

# Chain nodes with >> operator
create = CreateMemoryNode()
update = UpdateSalienceNode()
synthesize = SynthesizeCloudsNode()

# Sequential flow
memory_workflow = create >> update >> synthesize

# Conditional flow
memory_workflow = create >> (update - "needs_synthesis" >> synthesize)
```

**Node Lifecycle:**
- `prep_async(shared)`: Prepare inputs from shared state
- `exec_async(prep_res)`: Execute the core logic
- `post_async(shared, prep_res, exec_res)`: Post-process and return action

**Chaining Syntax:**
- `node1 >> node2`: Sequential (run node1, then node2)
- `node1 - "action_name" >> node2`: Conditional (if node1 returns "action_name", go to node2)

## Phoenix Cloud Observability

Brain OS includes real-time observability through Phoenix Cloud (Arize) integration for tracking tool usage, performance, and debugging.

### Setup

Phoenix Cloud is configured via environment variables:
```env
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-space-id
PHOENIX_API_KEY=your-api-key
```

Get your free account at: https://phoenix.arize.com/

### What Gets Traced

When enabled, all MCP tool calls are automatically traced with:
- **Input Parameters**: All function parameters (content, sector, salience, entities, observations)
- **Output Results**: Tool return values (memory ID, timestamps, success status)
- **Performance Metrics**: Execution time, latency measurements
- **Error Tracking**: Exception details and stack traces

### Implementation

Tracing is implemented using the `@instrument_mcp_tool` decorator in `src/utils/observability.py`:

```python
from src.utils.observability import instrument_mcp_tool

@mcp.tool
@instrument_mcp_tool("create_memory")
async def create_memory(...) -> str:
    # Tool logic
    # Automatically traced: inputs, outputs, performance, errors
```

### Phoenix Dashboard

View traces in real-time at your Phoenix Cloud dashboard:
- **Traces**: Individual tool executions with full context
- **Spans**: Hierarchical view of operations
- **Attributes**: Input/output parameters, performance metrics
- **Errors**: Exception details with full stack traces

### Data Captured

Example trace data for `create_memory`:
```json
{
  "mcp": {"tool": "create_memory", "success": true},
  "input": {
    "content": "Deploy the application using docker compose",
    "sector": "Procedural",
    "salience": 0.7,
    "memory_type": "instinctive",
    "entities_count": 2,
    "entities_items": "[\"docker\", \"compose\"]"
  },
  "output": {
    "result": "Memory stored successfully! - Neo4j ID: 67..."
  }
}
```

### Safety Limits

- Strings: 1000 chars (input), 2000 chars (output)
- Lists: First 10 items shown
- Large data is truncated with `_truncated: true` flag

### Key Files

- `src/utils/observability.py`: Phoenix tracing setup and decorators
- `src/tools/memory/create_memory.py`: Example tool with tracing

## Troubleshooting

### Coolify/Docker Deployment Issues

**Problem: Neo4j "Unrecognized setting" errors**
```
Failed to read config: Unrecognized setting with name: URI
```
- **Cause**: Coolify applies ALL environment variables to ALL containers in a docker-compose file
- **Solution**: ✅ FIXED - Neo4j is now deployed separately, not in the same docker-compose
- **Action Required**: Deploy Neo4j as a separate Coolify service and set `NEO4J_URI` to point to it

**Problem: Neo4j connection refused / DNS resolution failed**
```
Failed to DNS resolve address neo4j:7687
```
- **Cause**: Neo4j is not running or not accessible
- **Solution**: Deploy Neo4j separately and configure `NEO4J_URI` correctly in BrainOS environment variables

**Problem: HTTPS domain returns "no available server"**
- **Cause**: Using `ports` instead of `expose` in docker-compose.yml conflicts with Coolify's reverse proxy routing
- **Solution**: ✅ FIXED - Now uses `expose` directive (internal only) to match chrome-mcp pattern
- **Technical Details**: Coolify's HTTPS proxy needs to connect to container ports internally. Publishing ports to the host with `ports:` causes routing conflicts. Using `expose:` keeps ports internal while allowing Coolify's proxy to connect properly.

### Local Testing

**Note**: Since ports are now `expose`d (internal only), for local testing you need to either:

1. **Temporarily publish ports** - Change `expose:` to `ports:` in docker-compose.yml:
```yaml
ports:
  - "9131:9131"  # Temporary for local testing
```

2. **Test from within Docker network**:
```bash
docker compose up --build
docker exec brainos-server curl http://localhost:9131/health  # Should return {"status":"healthy"}
```

**For Coolify deployment**, keep `expose:` as-is - the proxy will connect internally.

### Common Issues

| Issue | Solution |
|-------|----------|
| `Module not found` | Run `uv sync` to install dependencies |
| Neo4j connection refused | ✅ Deploy Neo4j separately - see "Neo4j Deployment Guide" section |
| Neo4j "Unrecognized setting" errors | ✅ FIXED - Neo4j now deployed separately, not in docker-compose |
| MCP tools not visible | Check FastMCP server logs for errors |
| Port 8000 already in use | ✅ Changed to port 9131 - update local configs if needed |
| HTTPS returns "no available server" | ✅ FIXED - Now uses `expose` instead of `ports` (chrome-mcp pattern) |
| Coolify deployment fails | Ensure environment variables are set in Coolify, not in `.env` file |
| Can't access localhost:9131 locally | Ports are internal only - see Local Testing section for options |
