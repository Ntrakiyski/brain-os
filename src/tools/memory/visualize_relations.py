"""
Visualize Relations Tool.
MCP tool for visualizing relationships between bubbles as Mermaid diagrams.
"""

import logging

from pydantic import Field

from src.database.connection import get_driver

logger = logging.getLogger(__name__)


def register_visualize_relations(mcp) -> None:
    """Register the visualize_relations tool with FastMCP."""

    @mcp.tool
    async def visualize_relations(
        bubble_id: str = Field(
            description="Simple numeric Bubble ID (e.g., '4'). Get this from get_memory or get_all_memories results."
        ),
        depth: int = Field(
            default=2,
            description="How many hops to explore (1-4). Use 1 for direct connections, 2-3 for broader context, 4 for comprehensive exploration",
            ge=1,
            le=4
        ),
        format: str = Field(
            default="mermaid",
            description="Output format. Use 'mermaid' for inline diagrams, 'neo4j' for interactive graph exploration at http://localhost:7474"
        ),
    ) -> str:
        """
        Visualize connections between memories.

        **Use this to understand knowledge clusters and explore relationships.**

        Finding Bubble IDs:
        - Run get_all_memories() - IDs are simple numbers like "4"
        - Run get_memory(query="your search") - IDs shown in results
        - Just use the numeric ID shown in the output

        Relationship Types:
        - **explains**: Rationale or justification
        - **benefits**: Positive outcome or advantage
        - **contradicts**: Conflict or disagreement
        - **relates_to**: General association

        When to Use This:
        ✓ Understanding how memories connect
        ✓ Exploring related concepts
        ✓ Finding unexpected connections
        ✓ Interactive graph analysis (use format="neo4j")

        When NOT to Use This:
        ✗ Quick memory lookup (use get_memory)
        ✗ Sector overview (use list_sectors)
        ✗ Pattern recognition (use visualize_memories)

        Output Formats:
        - **mermaid**: Inline diagram (up to 20 connections shown)
        - **neo4j**: Cypher query for Neo4j Browser at http://localhost:7474

        Example Usage:
        1. get_all_memories(limit=10) → Find ID: "4"
        2. visualize_relations(bubble_id="4", depth=2) → See connections
        3. visualize_relations(bubble_id="4", format="neo4j") → Explore interactively
        """
        try:
            # Extract numeric ID from various bubble_id formats
            # Handles: "4", "4:abc123:14", "4:abc123-def456:14", etc.
            bubble_id_numeric = str(bubble_id).split(":")[0]
            try:
                bubble_id_numeric = int(bubble_id_numeric)
            except ValueError:
                return f"""## Error

Invalid bubble ID format: '{bubble_id}'

**Expected format:**
- Simple numeric ID like "4" or "123"

**To find bubble IDs**:
- Use get_memory to search for memories
- Use get_all_memories to see all memories
- Look for the simple numeric ID shown in the results
"""

            driver = await get_driver()

            if format == "neo4j":
                # Return Neo4j Browser query format
                return f"""## Neo4j Browser Visualization

**Bubble ID**: {bubble_id_numeric}
**Depth**: {depth} hops

### Neo4j Browser Query

Copy this into Neo4j Browser (http://localhost:7474):

```cypher
MATCH path = (b:Bubble) -[*1..{depth}] - (related:Bubble)
WHERE id(b) = {bubble_id_numeric}
AND b.valid_to IS NULL
AND related.valid_to IS NULL
RETURN path
```

This will show an interactive graph with all connected memories.
"""
            else:
                # Mermaid format - query Neo4j for relationships
                # Simplified query: only direct relationships (depth 1)
                query = """
                    MATCH (center:Bubble)
                    WHERE id(center) = $bubble_id
                    AND center.valid_to IS NULL
                    OPTIONAL MATCH (center)-[r:LINKED]->(related:Bubble)
                    WHERE related.valid_to IS NULL
                    RETURN center,
                           collect(DISTINCT {
                               bubble: related,
                               relation_type: r.type
                           }) as connections
                """

                async with driver.session() as session:
                    result = await session.run(query, bubble_id=bubble_id_numeric)
                    record = await result.single()

                    if not record:
                        return f"""## Error

No bubble found with ID: {bubble_id_numeric}

**To find bubble IDs**:
- Use get_memory to search for memories
- Use get_all_memories to see all memories
- Look for the simple numeric ID shown in the results
"""
                    center = dict(record["center"])
                    connections = record["connections"]

                    # Filter out null entries (when no relationships exist)
                    connections = [c for c in connections if c.get("bubble") is not None]

                    # If no relationships exist, show a helpful message
                    if not connections:
                        return f"""## Memory Relationships: No Connections Found

**Bubble ID**: {bubble_id}
**Content**: {center.get('content', '')[:100]}...
**Depth**: {depth} hops

### No Relationships Found

This memory has no explicit connections to other memories yet.

**What this means:**
- Relationships are created explicitly between related memories
- Use `get_memory_relations` to find related content by context
- This memory exists but isn't linked to others via explicit relationships

### To Explore Related Content:

Try these tools instead:
- **get_memory_relations(query="related topic")** - Finds related memories by content
- **get_memory(query="keyword")** - Search for specific keywords
- **get_all_memories()** - Browse all memories

### Neo4j Browser Query

To manually explore in Neo4j Browser (http://localhost:7474):

```cypher
MATCH (b:Bubble)
WHERE id(b) = {bubble_id}
RETURN b
```
"""

                    # Center node
                    center_content = center.get("content", "")[:30]
                    center_label = f"{bubble_id_numeric}: {center_content}..."
                    mermaid += f'    B1["{center_label}"]\n'

                    # Connection nodes
                    for i, conn in enumerate(connections[:20], 2):  # Limit to 20
                        bubble = conn["bubble"]
                        relation = conn["relation_type"]

                        node_id = f"B{i}"
                        content = bubble.get("content", "")[:30]
                        label = f"{str(bubble.element_id)[:8]}: {content}..."
                        mermaid += f'    {node_id}["{label}"]\n'
                        mermaid += f'    B1 -->|{relation or "relates"}| {node_id}\n'

                    return f"""## Memory Relationships

**Bubble ID**: {bubble_id}
**Content**: {center.get('content', '')[:100]}...
**Depth**: {depth} hops
**Found**: {len(connections)} relationships

### Mermaid Diagram

```mermaid
{mermaid}
```

### Neo4j Browser Query

For interactive exploration, copy this into Neo4j Browser:

```cypher
MATCH path = (b:Bubble) -[*1..{depth}] - (related:Bubble)
WHERE id(b) = {bubble_id}
AND b.valid_to IS NULL
AND related.valid_to IS NULL
RETURN path
```
"""

        except ValueError as e:
            # Handle invalid bubble_id format
            return f"""## Error

Invalid bubble ID format: {bubble_id}

**Bubble IDs must be numeric** (e.g., "4", "123").

**To find valid bubble IDs**:
- Use get_memory to search for memories
- The ID is shown in the results
"""
        except Exception as e:
            logger.error(f"Failed to visualize relations: {e}", exc_info=True)
            return f"Error visualizing relations: {str(e)}"
