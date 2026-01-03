"""
Brain OS MCP Server
Entry point for FastMCP CLI with proper path handling.
"""

import sys
from pathlib import Path

# Add project root to Python path BEFORE any imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import FastMCP and tools
from fastmcp import FastMCP
from pydantic import Field

# Import with lazy loading to avoid startup issues
def _get_queries():
    from src.database.queries import upsert_bubble, search_bubbles, get_all_bubbles
    return upsert_bubble, search_bubbles, get_all_bubbles

def _get_schemas():
    from src.utils.schemas import BubbleCreate
    return BubbleCreate

# Create FastMCP instance
mcp = FastMCP("Brain OS")

@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    sector: str = Field(description="Cognitive sector: Episodic, Semantic, Procedural, Emotional, or Reflective"),
    source: str = Field(default="direct_chat", description="Origin of the data"),
    salience: float = Field(default=0.5, description="Importance score from 0.0 to 1.0"),
) -> str:
    """Store a new memory in the Synaptic Graph."""
    try:
        BubbleCreate = _get_schemas()
        upsert_bubble, _, _ = _get_queries()
        bubble_data = BubbleCreate(content=content, sector=sector, source=source, salience=salience)
        result = await upsert_bubble(bubble_data)
        return f"Memory stored! ID: {result.id}, Sector: {result.sector}, Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool
async def get_memory(query: str = Field(description="Search term"), limit: int = Field(default=10)) -> str:
    """Retrieve memories from the Synaptic Graph with full content."""
    try:
        _, search_bubbles, _ = _get_queries()
        results = await search_bubbles(query, limit)
        if not results:
            return f"No memories found for '{query}'"
        output = [f"Found {len(results)} memories matching '{query}':\n\n"]
        for i, b in enumerate(results, 1):
            output.append(f"{i}. [{b.sector}] Salience: {b.salience:.2f}\n")
            output.append(f"   Created: {b.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            output.append(f"   Content: {b.content}\n")
            output.append(f"   Source: {b.source}\n")
            output.append("-" * 50 + "\n")
        return "".join(output)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool
async def list_sectors() -> str:
    """List all cognitive sectors."""
    return """Brain OS Five-Sector Ontology:
- Episodic: Events and experiences
- Semantic: Hard facts and knowledge
- Procedural: Habits and workflows
- Emotional: Sentiment and vibe
- Reflective: Meta-memory"""

@mcp.tool
async def get_all_memories(limit: int = Field(default=50, ge=1, le=200)) -> str:
    """Retrieve all memories from the Synaptic Graph with full content."""
    try:
        _, _, get_all_bubbles = _get_queries()
        results = await get_all_bubbles(limit)
        if not results:
            return "No memories stored yet."

        output = [f"Total: {len(results)} memories\n\n"]
        for i, b in enumerate(results, 1):
            output.append(f"{i}. [{b.sector}] Salience: {b.salience:.2f}\n")
            output.append(f"   Created: {b.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            output.append(f"   Content: {b.content}\n")
            output.append(f"   Source: {b.source}\n")
            output.append("-" * 50 + "\n")
        return "".join(output)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool
async def visualize_memories(limit: int = Field(default=50, ge=1, le=200)) -> str:
    """Generate a visual chart of memory distribution and statistics."""
    try:
        _, _, get_all_bubbles = _get_queries()
        results = await get_all_bubbles(limit)
        if not results:
            return "No memories to visualize."
        sector_counts = {}
        for b in results:
            sector_counts[b.sector] = sector_counts.get(b.sector, 0) + 1
        output = ["\n" + "=" * 50 + "\nBRAIN OS MEMORY VISUALIZATION\n" + "=" * 50 + "\n"]
        output.append(f"Total Memories: {len(results)}\n\nSector Distribution:\n")
        for sector in ["Episodic", "Semantic", "Procedural", "Emotional", "Reflective"]:
            count = sector_counts.get(sector, 0)
            if count > 0:
                output.append(f"  {sector}: {'█' * count} {count}\n")
        return "".join(output)
    except Exception as e:
        return f"Error: {str(e)}"
