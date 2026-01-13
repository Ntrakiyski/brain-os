"""
Brain OS MCP Server
Minimal entry point with modular tool registration.
"""

import logging
import os
import sys
from pathlib import Path

from fastmcp import FastMCP
from starlette.responses import JSONResponse

# Add project root to Python path BEFORE any imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import tool registration functions
from src.tools import register_memory_tools, register_agent_tools
from src.tools.notifications import register_notification_tools
from src.tools.monitoring import register_monitoring_tools

# Create FastMCP instance with comprehensive instructions
mcp = FastMCP(
    "Brain OS",
    instructions="""
    You are interacting with Brain OS, a cognitive operating system designed as a symbiotic AI-human system.

    ## CORE PHILOSOPHY
    Brain OS uses a "metabolic thinking" approach where the AI handles memory, retrieval, and synthesis while the human provides strategic direction.

    ## THE FIVE-SECTOR ONTOLOGY
    All memories are organized across 5 cognitive sectors:
    - **Episodic**: Personal experiences, events ("Had meeting with client")
    - **Semantic**: Facts, decisions, knowledge ("FastAPI is async framework")
    - **Procedural**: Skills, how-to, workflows ("Deploy with Docker Compose")
    - **Emotional**: Feelings, reactions ("Frustrated by scope creep")
    - **Reflective**: Insights, learnings ("Learned to lock requirements early")

    ## MEMORY TYPES AND THE OVEN ANALOGY
    Think of instinctive memory like a hot oven - when you walk near it, you automatically know it's hot without thinking about it.

    **memory_type options:**
    - "instinctive": Auto-activates based on context (like the hot oven analogy)
    - "thinking": Requires explicit recall (default, most memories)
    - "dormant": Rarely activates, for archives/reference material

    **When to mark a memory as instinctive:**
    ✓ Technology stack choices
    ✓ Pricing structures and rates
    ✓ Deployment procedures
    ✓ Client preferences
    ✗ One-time events
    ✗ Temporary information
    ✗ Meeting notes (use "thinking" instead)

    ## SALIENCE SCORING (0.0 to 1.0)
    Use the full range - don't default everything to 0.5:
    - 0.9-1.0: Business-critical decisions ("Chose startup over enterprise job")
    - 0.7-0.8: Important project details ("Client prefers iterative approval")
    - 0.5-0.6: Routine work information ("Team meeting on Tuesday")
    - 0.3-0.4: Nice-to-know details ("Considering VS Code extension")
    - 0.0-0.2: Temporary notes ("Remember to call Jim back")

    ## TOOL SELECTION GUIDE

    **Creating Memories:**
    - Use `create_memory` for ANY information worth remembering
    - Always include WHY in content, not just WHAT
    - Use observations for nuanced context, rationale, trade-offs
    - Keep entity names consistent across memories (e.g., always "FastTrack" not "fast track")

    **Retrieving Memories:**
    - `get_memory`: Quick keyword search when you know what you're looking for
    - `get_all_memories`: Get complete overview with statistics (good for starting work)
    - `get_instinctive_memory`: Context switching, starting work on a project
    - `get_memory_relations`: Deep contextual queries requiring synthesis
    - `summarize_project`: Project overview after returning from a break

    **Analysis and Visualization:**
    - `list_sectors`: Check cognitive balance (aim for 25-35% Semantic, 20-30% Procedural)
    - `visualize_memories`: See salience distribution at a glance
    - `visualize_relations`: Explore connections between specific memories

    ## COGNITIVE BALANCE CHECKS
    If the user seems overwhelmed or scattered:
    1. Suggest running `list_sectors()` to check cognitive balance
    2. Recommend sector rebalancing:
       - Too much Procedural? Add Reflective memories (insights)
       - Too much Semantic? Add Action (Procedural memories)
       - Too much Episodic? Add Learning (Reflective memories)

    ## BEST PRACTICES

    **Memory Creation:**
    - Include decision rationale in observations, not just content
    - Use consistent entity names across all memories
    - Set appropriate salience - don't default everything to 0.5
    - Only mark truly auto-relevant memories as instinctive

    **When User Asks for Help:**
    - For project questions: Use `get_memory_relations` with conversation history
    - For context switching: Use `get_instinctive_memory` first
    - For decision support: Retrieve past similar decisions first

    **Common Patterns:**
    - After meetings: Create Episodic memory + Semantic memories for decisions
    - Making decisions: Retrieve past decisions → Create new instinctive memory
    - Weekly review: `get_all_memories` → `list_sectors` → Create Reflective summary

    ## IMPORTANT REMINDERS
    - NEVER guess the sector - ask the user if unclear
    - ALWAYS explain why you're choosing a specific tool
    - Encourage storing observations separately from main content
    - Suggest instinctive memory sparingly - it's for auto-activation, not everything important
    """
)

# Add health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request) -> JSONResponse:
    """Health check endpoint for deployment monitoring."""
    return JSONResponse({"status": "healthy", "service": "brainos-mcp"})

# Register all tool modules
register_memory_tools(mcp)
register_agent_tools(mcp)
register_notification_tools(mcp)
register_monitoring_tools(mcp)


# =============================================================================
# RESOURCES - Static documentation LLMs can read
# =============================================================================

@mcp.resource("brainos://guide")
async def user_guide_resource() -> str:
    """Complete user guide for Brain OS best practices."""
    guide_path = project_root / "docs" / "COMPLETE_USER_GUIDE.md"
    if guide_path.exists():
        return guide_path.read_text()
    return "User guide not found. See docs/COMPLETE_USER_GUIDE.md"


@mcp.resource("brainos://philosophy")
async def philosophy_resource() -> str:
    """Core philosophy and concepts behind Brain OS."""
    return """
# Brain OS Philosophy

## The Symbiotic AI-Human Model
Brain OS implements a cognitive operating system where:
- **Human** provides strategic direction ("The Brand")
- **AI** handles metabolic thinking (memory, retrieval, synthesis)

## Five-Sector Ontology
Memories are organized across cognitive sectors:
- **Episodic**: What happened (events, meetings)
- **Semantic**: What is true (facts, decisions, knowledge)
- **Procedural**: How to do things (skills, workflows)
- **Emotional**: How it felt (reactions, responses)
- **Reflective**: What was learned (insights, patterns)

## Bubbles and Clouds
- **Bubbles**: Raw episodic memories (user input)
- **Clouds**: AI-generated insights and syntheses

## Salience Scoring
Memories decay over time but reinforce through access. Salience (0.0-1.0) determines:
- Initial importance
- Retrieval priority
- Resistance to decay

## Neurochain Architecture
- Single-waypoint connections (no multi-hop)
- Synaptic weights on relationships
- Temporal validity windows (valid_from, valid_to)
"""


@mcp.resource("brainos://tool-reference")
async def tool_reference_resource() -> str:
    """Quick reference for all available tools."""
    return """
# Brain OS Tool Reference

## Memory Management
- **create_memory**: Store information with sector, salience, entities
- **get_memory**: Quick keyword search
- **get_all_memories**: Complete overview with statistics

## Advanced Retrieval (Phase 3)
- **get_instinctive_memory**: Auto-activate based on context (Oven Analogy)
- **get_memory_relations**: Deep contextual retrieval with synthesis
- **visualize_relations**: Explore connections between memories

## Analysis
- **list_sectors**: Cognitive sector distribution
- **visualize_memories**: Visual representation of memory patterns

## Agents
- **summarize_project**: AI-powered project summaries

## Deletion
- **delete_memory**: Delete specific memory by ID (requires confirm=True)
- **delete_all_memories**: Delete all memories (requires confirm="DELETE_ALL")

## Decision Guide
| Need | Use |
|------|-----|
| Store info | create_memory |
| Quick lookup | get_memory |
| Start work | get_instinctive_memory |
| Deep understanding | get_memory_relations |
| Project overview | summarize_project |
| Check balance | list_sectors |
| Delete memory | delete_memory |
"""


@mcp.resource("brainos://prompts")
async def prompts_resource() -> str:
    """Available prompt templates for common workflows."""
    return """
# Brain OS Prompt Templates

These are reusable prompt templates. To use them, ask Claude to run a specific prompt by name.

## Available Prompts

### 1. weekly_review
**Use for:** End-of-week cognitive review and synthesis

**How to use:**
```
"Use the weekly_review prompt"
"Help me do a weekly review"
```

**What it does:**
- Gets overview of all memories (limit=100)
- Checks sector balance with list_sectors()
- Visualizes patterns with visualize_memories()
- Extracts key themes with get_memory_relations()
- Creates Reflective summary memory

**Best time:** Friday evening or Sunday evening

---

### 2. project_start
**Use for:** Loading context when starting work on a project

**How to use:**
```
"Use the project_start prompt for FastTrack"
"I'm starting work on Project A, use the project_start prompt"
```

**What it does:**
- Asks for project name
- Runs get_instinctive_memory for auto-activation
- Runs get_memory for recent project memories
- Runs summarize_project for overview
- Identifies knowledge gaps

**Best time:** Monday morning, returning from break, context switching

---

### 3. decision_support
**Use for:** Making decisions using past experience

**How to use:**
```
"Use the decision_support prompt to help me choose between X and Y"
"I need to make a decision, use the decision_support prompt"
```

**What it does:**
- Asks what decision you're making
- Searches for past similar decisions
- Uses get_memory_relations for deep context
- Synthesizes patterns from past decisions
- Offers to store new decision as instinctive memory

**Best time:** Before making important choices

---

### 4. cognitive_balance
**Use for:** Checking and rebalancing cognitive state

**How to use:**
```
"Use the cognitive_balance prompt"
"Check my cognitive balance"
"Am I cognitively balanced?"
```

**What it does:**
- Runs list_sectors() to see distribution
- Runs visualize_memories() for patterns
- Analyzes balance against ideal distribution
- Identifies imbalances
- Suggests specific memory types to create
- Offers to help create balancing memories

**Best time:** Feeling scattered, overwhelmed, or stuck

## Prompt Usage Tips

1. **Be specific**: "Use the weekly_review prompt" works better than "help me review"
2. **Provide context**: For project_start and decision_support, give project/decision details
3. **Act on suggestions**: Prompts will suggest creating memories - follow through
4. **Weekly routine**: Make weekly_review a Friday/Sunday habit

## Ideal Cognitive Distribution

When using cognitive_balance prompt, aim for:
- Semantic: 25-35% (facts, decisions, knowledge)
- Procedural: 20-30% (skills, workflows)
- Episodic: 15-25% (events, experiences)
- Emotional: 5-15% (feelings, reactions)
- Reflective: 5-15% (insights, learnings)
"""


# =============================================================================
# DYNAMIC VISUALIZATION RESOURCES
# =============================================================================

@mcp.resource("brainos://visualize/sectors{?format}")
async def sectors_visualization_resource(format: str = "ascii") -> str:
    """Generate sector distribution visualization. format: 'ascii' (default) or 'json'."""
    from src.database.connection import get_driver
    from src.database.queries.memory import get_bubble_count

    driver = await get_driver()

    # Get sector counts
    sectors = ["Episodic", "Semantic", "Procedural", "Emotional", "Reflective"]
    counts = {}
    total = 0

    for sector in sectors:
        count = await get_bubble_count(driver, sector)
        counts[sector] = count
        total += count

    if total == 0:
        return "No memories found in the Synaptic Graph."

    if format.lower() == "json":
        import json
        return json.dumps({
            "total": total,
            "sectors": {
                sector: {
                    "count": counts[sector],
                    "percentage": round((counts[sector] / total) * 100, 1)
                }
                for sector in sectors
            }
        }, indent=2)

    # ASCII visualization
    lines = []
    lines.append(f"Brain OS Cognitive Distribution (Total: {total} memories)")
    lines.append("=" * 50)

    for sector in sectors:
        count = counts[sector]
        percentage = (count / total) * 100
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        lines.append(f"{sector:12} |{bar:<50} {count} ({percentage:.1f}%)")

    lines.append("=" * 50)
    lines.append("\nIdeal Distribution:")
    lines.append("  Semantic:     25-35%")
    lines.append("  Procedural:   20-30%")
    lines.append("  Episodic:     15-25%")
    lines.append("  Emotional:     5-15%")
    lines.append("  Reflective:    5-15%")

    return "\n".join(lines)


@mcp.resource("brainos://visualize/relations/{bubble_id}")
async def relations_visualization_resource(bubble_id: str) -> str:
    """Generate Mermaid diagram for a memory's relationships."""
    from src.database.connection import get_driver
    from neo4j import AsyncGraphDatabase

    driver = await get_driver()

    # Extract numeric ID from various formats
    import re
    match = re.search(r'\d+', bubble_id)
    if not match:
        return "Error: Invalid bubble ID format. Please provide a numeric ID."
    numeric_id = int(match.group())

    query = """
        MATCH (b:Bubble)
        WHERE id(b) = $id AND b.valid_to IS NULL
        OPTIONAL MATCH (b)-[r:LINKED]->(other:Bubble)
        WHERE other.valid_to IS NULL
        RETURN b, collect({
            id: id(other),
            content: other.content,
            sector: other.sector,
            type: r.type
        }) as relations
    """

    async with driver.session() as session:
        result = await session.run(query, id=numeric_id)
        record = await result.single()

        if not record:
            return f"Memory with ID {numeric_id} not found."

        node = record["b"]
        relations = record["relations"]

        # Build Mermaid diagram
        lines = []
        lines.append("```mermaid")
        lines.append("graph LR")
        lines.append(f'    Center["{node["sector"]}<br/>"{node["content"][:40]}...""]')
        lines.append("    Center(Center)")

        for i, rel in enumerate(relations[:10], 1):  # Limit to 10 relations
            target_id = rel["id"]
            content = rel["content"][:30]
            sector = rel["sector"]
            rel_type = rel["type"]
            lines.append(f'    Node{i}["{sector}<br/>{content}...""]')
            lines.append(f'    Center -->|{rel_type}| Node{i}')

        if len(relations) > 10:
            lines.append(f"    More[\"...and {len(relations) - 10} more\"]")
            lines.append("    Center -.-> More")

        lines.append("```")
        lines.append("")
        lines.append(f"**Total Relations:** {len(relations)}")
        lines.append("")
        lines.append("**Neo4j Browser Query:**")
        lines.append(f"```cypher")
        lines.append(f'MATCH (b)-[r:LINKED]->(other)')
        lines.append(f'WHERE id(b) = {numeric_id}')
        lines.append(f'RETURN b, r, other')
        lines.append(f"```")

        return "\n".join(lines)


# =============================================================================
# PROMPTS - Reusable prompt templates
# =============================================================================

@mcp.prompt
async def weekly_review() -> str:
    """Generate a structured weekly review of all memories."""
    return """Please help me with a weekly review of my Brain OS memories.

Follow this structure:
1. **Overview**: Run get_all_memories(limit=100) to see everything
2. **Sector Balance**: Run list_sectors() to check cognitive distribution
3. **Visualization**: Run visualize_memories() to see patterns
4. **Key Themes**: Use get_memory_relations with query "What were the main themes this week?" and time_scope="recent"
5. **Synthesis**: Create a Reflective memory summarizing insights

For each insight you identify, ask if I want to store it as a Reflective memory."""


@mcp.prompt
async def project_start(project: str) -> str:
    """Prepare context when starting work on a project."""
    return f"""I'm starting work on a project: {project}

Help me load relevant context:
1. Run get_instinctive_memory("I'm starting work on {project}")
2. Run get_memory(query="{project}", limit=10)
3. Run summarize_project(project="{project}")
4. Identify gaps in my knowledge and suggest what to store

Return a concise context summary with:
- Project overview
- Key decisions
- Action items
- Missing information I should capture"""


@mcp.prompt
async def decision_support(decision: str) -> str:
    """Support decision-making by retrieving past context."""
    return f"""I need to make a decision: {decision}

Help me use past experience to inform it:
1. Search for past similar decisions: get_memory(query="{decision}")
2. Deep retrieval: get_memory_relations with context
3. Synthesize patterns from past decisions
4. After I decide, offer to store it as an instinctive Semantic memory

Extract from past decisions:
- What criteria mattered
- What trade-offs I accepted
- What I learned"""


@mcp.prompt
async def cognitive_balance() -> str:
    """Check and rebalance cognitive state."""
    return """Help me check my cognitive balance and suggest rebalancing.

Steps:
1. Run list_sectors() to see current distribution
2. Run visualize_memories() to see salience patterns
3. Analyze balance:
   - Ideal: Semantic 25-35%, Procedural 20-30%, Episodic 15-25%, Emotional 5-15%, Reflective 5-15%
4. Identify imbalances and suggest specific memory types to add
5. Offer to create Reflective memories to process other sectors

For each imbalance:
- Explain why it matters
- Suggest 3 specific memories to create
- Offer to help create them"""


# =============================================================================
# SERVER ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Get port from environment or use default
    port = int(os.getenv("MCP_PORT", 9131))
    host = os.getenv("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting Brain OS MCP Server on {host}:{port}...")
    logger.info("Available tools:")
    logger.info("  - create_memory: Store a new memory in the Synaptic Graph")
    logger.info("  - get_memory: Retrieve memories by search query")
    logger.info("  - get_all_memories: Retrieve all memories")
    logger.info("  - list_sectors: List all cognitive sectors")
    logger.info("  - visualize_memories: Generate memory distribution chart")
    logger.info("  - summarize_project: Summarize project memories using AI")
    logger.info("")
    logger.info("Phase 3 Tools:")
    logger.info("  - get_instinctive_memory: Auto-activate memories based on context")
    logger.info("  - get_memory_relations: Deep retrieval with contextual understanding")
    logger.info("  - visualize_relations: Visualize relationships between memories")
    logger.info("")
    logger.info("Deletion Tools:")
    logger.info("  - delete_memory: Delete a specific memory by ID")
    logger.info("  - delete_all_memories: Delete all memories (requires confirmation)")
    logger.info("")
    logger.info("Resources:")
    logger.info("  - brainos://guide: Complete user guide")
    logger.info("  - brainos://philosophy: Core philosophy and concepts")
    logger.info("  - brainos://tool-reference: Quick tool reference")
    logger.info("  - brainos://prompts: Prompt templates guide")
    logger.info("  - brainos://visualize/sectors: Sector distribution visualization")
    logger.info("  - brainos://visualize/relations/{id}: Relationship diagrams")
    logger.info("")
    logger.info("Prompts:")
    logger.info("  - weekly_review: Structured weekly review workflow")
    logger.info("  - project_start: Context loading when starting work")
    logger.info("  - decision_support: Decision-making using past experience")
    logger.info("  - cognitive_balance: Check and rebalance cognitive state")
    logger.info(f"Health check: http://{host}:{port}/health")

    # Run the server directly (compatible with Coolify HTTPS termination)
    mcp.run(transport="http", host=host, port=port)
