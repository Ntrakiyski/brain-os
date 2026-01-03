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
- **Runtime**: Python 3.14+ with `uv` package manager
- **MCP Framework**: FastMCP 2.x for tools, background tasks, and remote proxy mounting
- **Agent Framework**: PocketFlow (100-line minimalist framework) for workflow orchestration
- **Database**: Neo4j Community Edition for the Synaptic Graph
- **Intelligence**: Dual-LLM architecture
  - **Groq**: Fast actions (classification, extraction, routing) - speed and cost efficiency
  - **OpenRouter**: Deep thinking (research, synthesis, complex reasoning) - quality and intelligence

## Development Commands

### Setup
```bash
# Add dependencies
uv add fastmcp pocketflow neo4j python-dotenv pydantic groq

# Verify FastMCP installation
fastmcp version
```

### Running Servers
```bash
# Start Neo4j Docker container (required first)
docker-compose up -d

# Neo4j Browser available at: http://localhost:7474

# Run main MCP server with stdio (default)
fastmcp run brainos_server.py:mcp

# Run with HTTP transport for remote access
fastmcp run brainos_server.py:mcp --transport http --port 8000

# Run demo server
fastmcp run fastmcp_demo_app/my_server.py:mcp
python fastmcp_demo_app/test_client.py
```

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
# Neo4j (local Docker instance)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>

# Groq (fast actions)
GROQ_API_KEY=<your-groq-key>
GROQ_QUICK_MODEL=openai/gpt-oss-120b

# OpenRouter (deep thinking)
OPENROUTER_API_KEY=<your-openrouter-key>
OPENROUTER_RESEARCHING_MODEL=anthropic/claude-sonnet-4
OPENROUTER_THINKINIG_MODEL=anthropic/claude-sonnet-4
OPENROUTER_CREATIVE_MODEL=anthropic/claude-sonnet-4
OPENROUTER_PLANNING_MODEL=anthropic/claude-opus-4
```

## Architecture Overview

### Fractal DNA: Modular Hierarchy (Maps to PocketFlow)
- **Cells** → `AsyncNode.exec()`: Atomic utility functions (LLM calls, schema validators)
- **Organs** → `AsyncFlow`: Specialized agent clusters (Researcher, Technical Auditor, Synthesizer)
- **Organisms** → Nested `AsyncFlow`: Multi-agent workflows (Ingestion, Weekly Synthesis)

### Project Structure (Phase 1 - Completed)
```
0brainos/
├── src/
│   ├── core/
│   │   └── config.py          # Environment variables & global settings (frozen dataclasses)
│   ├── database/
│   │   ├── connection.py      # Neo4j async driver with global connection singleton
│   │   └── queries.py         # Granular Cypher query functions (upsert, search, get_by_id)
│   ├── tools/
│   │   └── memory_tools.py    # FastMCP tool definitions (create, get, list_sectors)
│   ├── utils/
│   │   └── schemas.py         # Pydantic validation models
│   └── main.py                # Alternative entry point
├── brainos_server.py          # ROOT-level MCP server entry point for Claude Desktop
├── docker-compose.yml         # Neo4j container configuration
├── docs/project/phase1/       # Phase 1 documentation
│   ├── user-stories.md        # Implementation status
│   ├── code-snippets.md       # Key code patterns
│   └── phase-overview.md      # Architectural decisions
└── fastmcp_demo_app/          # FastMCP learning examples
```

### Key Concepts

**Memory Retrieval Scoring**: Composite formula with 60% similarity, 20% salience, 10% recency, 10% connection strength.

**Remote Proxy Mounting**: FastMCP can dynamically mount external MCP servers (Gmail, Calendar) via SSE/HTTP without code restart.

**Validity Windows**: Track temporal evolution with `valid_from` and `valid_to` timestamps for audit trails.

## Current Status

### Phase 1: ✅ COMPLETED
Phase 1 successfully established the foundational infrastructure:
- ✅ MCP server with 4 tools (`create_memory`, `get_memory`, `get_all_memories`, `list_sectors`)
- ✅ Neo4j integration with async connection pooling
- ✅ Claude Desktop integration via FastMCP CLI
- ✅ Configuration management with frozen dataclasses
- ✅ Pydantic validation for all data operations
- ✅ Memory visualization with sector distribution charts

See `docs/project/phase1/` for complete Phase 1 documentation and `docs/project/full_project_idea.md` for the master specification.

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
