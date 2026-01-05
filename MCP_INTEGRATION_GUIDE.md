# Brain OS MCP Integration Guide

This guide explains how to connect to and interact with your deployed Brain OS MCP server at `https://brainoz.worfklow.org/mcp`.

## Connection Methods

### Method 1: Interactive Python Client (Recommended for Testing)

Use the `brainos_interactive.py` script from your local machine:

```bash
# Test connection
python3 brainos_interactive.py test

# List all available tools
python3 brainos_interactive.py tools

# List cognitive sectors
python3 brainos_interactive.py sectors

# Create a memory
python3 brainos_interactive.py create Episodic "Discovered MCP integration works great"

# Search for memories
python3 brainos_interactive.py search "MCP"

# Get all memories
python3 brainos_interactive.py memories 20

# Visualize memory distribution
python3 brainos_interactive.py viz
```

### Method 2: Use as Python Module

Import and use the interactive client in Python scripts or REPL:

```python
from brainos_interactive import *

# Test connection
test()

# Create memories
create("Learning about brain architecture", "Semantic", 0.9)
create("Had a great meeting today", "Episodic", 0.7)

# Search memories
search("meeting", 5)

# Get all memories
memories(50)

# Visualize distribution
viz()
```

### Method 3: Claude Desktop Integration (Remote MCP)

You can add your deployed Brain OS server to Claude Desktop using the Remote Proxy pattern.

**Option A: Direct HTTP Connection**

Edit your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "brain-os-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/proxy",
        "https://brainoz.worfklow.org/mcp"
      ]
    }
  }
}
```

**Option B: Using MCP Proxy Tool**

```bash
# Install MCP proxy tool
npm install -g @modelcontextprotocol/proxy

# Test connection
mcp-proxy https://brainoz.worfklow.org/mcp
```

Then configure Claude Desktop:

```json
{
  "mcpServers": {
    "brain-os": {
      "command": "mcp-proxy",
      "args": ["https://brainoz.worfklow.org/mcp"]
    }
  }
}
```

### Method 4: FastMCP Client (Advanced)

For programmatic access with full FastMCP features:

```python
import asyncio
from fastmcp import Client

async def use_brainos():
    client = Client("https://brainoz.worfklow.org/mcp")

    async with client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Create a memory
        result = await client.call_tool("create_memory", {
            "content": "Testing FastMCP client integration",
            "sector": "Semantic",
            "salience": 0.8
        })
        print(result)

        # Search memories
        result = await client.call_tool("get_memory", {
            "query": "FastMCP",
            "limit": 10
        })
        print(result)

# Run
asyncio.run(use_brainos())
```

## Available Brain OS Tools

Your Brain OS server exposes these MCP tools:

1. **create_memory** - Store a new memory in the Synaptic Graph
   - `content` (string): The information to remember
   - `sector` (string): Episodic, Semantic, Procedural, Emotional, or Reflective
   - `source` (string, optional): Origin of the data
   - `salience` (float, optional): Importance score 0.0 to 1.0

2. **get_memory** - Search for memories
   - `query` (string): Search term
   - `limit` (int, optional): Max results (default: 10)

3. **get_all_memories** - Retrieve all memories
   - `limit` (int, optional): Max results (default: 50, max: 200)

4. **list_sectors** - List all cognitive sectors
   - No parameters

5. **visualize_memories** - Generate memory distribution chart
   - `limit` (int, optional): Max memories to analyze (default: 50, max: 200)

## Five-Sector Ontology

Brain OS organizes memories into five cognitive sectors:

- **Episodic**: Events and experiences (what happened)
- **Semantic**: Hard facts and knowledge (what is true)
- **Procedural**: Habits and workflows (how to do things)
- **Emotional**: Sentiment and vibe (how it feels)
- **Reflective**: Meta-memory (thinking about thinking)

## Examples

### Example 1: Daily Journal Entry

```python
from brainos_interactive import create

create("Team meeting went well, discussed Q1 goals", "Episodic", 0.7)
create("Feeling energized after the discussion", "Emotional", 0.6)
create("Action item: Review project timeline by Friday", "Procedural", 0.9)
```

### Example 2: Learning Session

```python
create("MCP enables seamless AI-human integration via tools", "Semantic", 0.9)
create("Successfully deployed Brain OS to production", "Episodic", 0.8)
create("Learned FastMCP supports HTTP transport with SSE", "Semantic", 0.8)
```

### Example 3: Research Workflow

```python
# Store research findings
create("Paper: Attention Is All You Need introduces Transformers", "Semantic", 1.0)
create("Watched Andrej Karpathy's transformer lecture", "Episodic", 0.7)

# Search related memories
search("transformer", 10)

# Visualize knowledge accumulation
viz()
```

## Troubleshooting

### Connection Issues

1. **Verify server is running:**
```bash
curl https://brainoz.worfklow.org/health
# Should return: {"status":"healthy","service":"brainos-mcp"}
```

2. **Test MCP endpoint:**
```bash
curl -X POST https://brainoz.worfklow.org/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

3. **Check network connectivity:**
   - Ensure no firewall blocking HTTPS traffic
   - Verify domain resolves correctly: `nslookup brainoz.worfklow.org`

### Common Errors

- **403 Forbidden**: Check server authentication settings
- **404 Not Found**: Verify URL is exactly `https://brainoz.worfklow.org/mcp`
- **Connection Timeout**: Check if server is deployed and running
- **CORS Errors**: MCP uses Server-Sent Events, ensure proper headers

## Next Steps

1. ✅ Server deployed at `https://brainoz.worfklow.org/mcp`
2. ✅ Client tools created (`brainos_interactive.py`, `simple_brainos_client.py`)
3. ⬜ Test connection from your local machine
4. ⬜ Integrate with Claude Desktop
5. ⬜ Build custom workflows using the Python client
6. ⬜ Extend with additional MCP tools as needed

## Additional Resources

- **Brain OS Documentation**: See `/docs/project/` for full architecture
- **FastMCP Docs**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io
- **CLAUDE.md**: Project-specific guidance for Claude Code

---

**Brain OS** - Cognitive Operating System for Personal and Professional Intelligence
