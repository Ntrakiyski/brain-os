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
            description="Bubble ID (element_id) to visualize relationships for"
        ),
        depth: int = Field(
            default=2,
            description="How many hops to explore (1-4 recommended)",
            ge=1,
            le=4
        ),
        format: str = Field(
            default="mermaid",
            description="Output format: 'mermaid' for diagram, 'neo4j' for browser query"
        ),
    ) -> str:
        """
        Visualize relationships between bubbles.

        Returns either:
        - Mermaid diagram code for inline visualization
        - Neo4j Browser query for interactive exploration

        Relationships show how memories connect:
        - **explains**: Rationale or justification
        - **benefits**: Positive outcome or advantage
        - **contradicts**: Conflict or disagreement
        - **relates_to**: General association

        **Example**:
            Input: bubble_id="4", depth=2
            Output: Mermaid diagram showing connections up to 2 hops away

        **Neo4j Browser**:
        For interactive exploration, copy the provided Cypher query into:
        http://localhost:7474
        """
        try:
            driver = get_driver()

            if format == "neo4j":
                # Return Neo4j Browser query format
                return f"""## Neo4j Browser Visualization

**Bubble ID**: {bubble_id}
**Depth**: {depth} hops

### Neo4j Browser Query

Copy this into Neo4j Browser (http://localhost:7474):

```cypher
MATCH path = (b:Bubble) -[*1..{depth}] - (related:Bubble)
WHERE element_id(b) = {bubble_id}
AND b.valid_to IS NULL
AND related.valid_to IS NULL
RETURN path
```

This will show an interactive graph with all connected memories.
"""
            else:
                # Mermaid format - query Neo4j for relationships
                query = """
                    MATCH (center:Bubble)
                    WHERE element_id(center) = $bubble_id
                    MATCH path = (center)-[r:LINKED*1..{depth}]-(related:Bubble)
                    WHERE related.valid_to IS NULL
                    RETURN center,
                           collect(DISTINCT {{
                               bubble: related,
                               relation_type: head([(center)-[r:LINKED]-(related) | r.type])
                           }}) as connections
                """

                async with driver.session() as session:
                    result = await session.run(query, bubble_id=int(bubble_id), depth=depth)
                    record = await result.single()

                    if not record:
                        return f"""## Error

No bubble found with ID: {bubble_id}

**To find bubble IDs**:
- Use get_memory to search for memories
- Use get_all_memories to see all memories
- The ID is shown in parentheses in results
"""
                    center = dict(record["center"])
                    connections = record["connections"]

                    # Build Mermaid diagram
                    mermaid = "graph LR\n"

                    # Center node
                    center_content = center.get("content", "")[:30]
                    center_label = f"{bubble_id[:8]}: {center_content}..."
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
WHERE element_id(b) = {bubble_id}
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
