"""
FastMCP tools for Brain OS memory operations.
Exposes create_memory and get_memory to Claude.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP
from pydantic import Field

logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("Brain OS")


def _get_queries():
    """Lazy import queries to avoid startup issues."""
    from src.database.queries import upsert_bubble, search_bubbles, get_all_bubbles
    return upsert_bubble, search_bubbles, get_all_bubbles


def _get_schemas():
    """Lazy import schemas to avoid startup issues."""
    from src.utils.schemas import BubbleCreate
    return BubbleCreate


@mcp.tool
async def create_memory(
    content: str = Field(description="The information to remember"),
    sector: str = Field(description="Cognitive sector: Episodic, Semantic, Procedural, Emotional, or Reflective"),
    source: str = Field(default="direct_chat", description="Origin of the data (e.g., transcript, direct_chat)"),
    salience: float = Field(default=0.5, description="Importance score from 0.0 to 1.0"),
) -> str:
    """
    Store a new memory in the Synaptic Graph.

    Creates a Bubble node with automatic timestamp tracking.
    Use this to preserve important context across sessions.
    """
    try:
        # Lazy imports
        BubbleCreate = _get_schemas()
        upsert_bubble, _ = _get_queries()

        # Validate and create the bubble
        bubble_data = BubbleCreate(
            content=content,
            sector=sector,
            source=source,
            salience=salience
        )
        result = await upsert_bubble(bubble_data)

        return (
            f"Memory stored successfully!\n"
            f"- ID: {result.id}\n"
            f"- Sector: {result.sector}\n"
            f"- Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"- Salience: {result.salience}\n"
            f"- Content: {result.content[:100]}{'...' if len(result.content) > 100 else ''}"
        )
    except Exception as e:
        logger.error(f"Failed to create memory: {e}")
        return f"Error storing memory: {str(e)}"


@mcp.tool
async def get_memory(
    query: str = Field(description="The search term to find matching memories"),
    limit: int = Field(default=10, description="Maximum number of results to return"),
) -> str:
    """
    Retrieve memories from the Synaptic Graph based on a keyword search.

    Returns bubbles matching the query, ordered by recency.
    Use this to recall previously stored context.
    """
    try:
        # Lazy imports
        _, search_bubbles = _get_queries()

        results = await search_bubbles(query, limit)

        if not results:
            return f"No memories found matching query: '{query}'"

        output = [f"Found {len(results)} memories matching '{query}':\n"]
        for i, bubble in enumerate(results, 1):
            output.append(
                f"\n{i}. ID: {bubble.id} | Sector: {bubble.sector} | "
                f"Salience: {bubble.salience:.2f}\n"
                f"   Created: {bubble.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"   Source: {bubble.source}\n"
                f"   Content: {bubble.content}"
            )

        return "\n".join(output)
    except Exception as e:
        logger.error(f"Failed to retrieve memory: {e}")
        return f"Error retrieving memory: {str(e)}"


@mcp.tool
async def list_sectors() -> str:
    """
    List all available cognitive sectors in the Brain OS ontology.

    Returns the five-sector ontology with descriptions.
    """
    sectors = {
        "Episodic": "Events and experiences (What happened and when)",
        "Semantic": "Hard facts and knowledge (Requirements, names, technical data)",
        "Procedural": "Habits and workflows (The 'My Way' protocol and brand behaviors)",
        "Emotional": "Sentiment and vibe (Tracking morale, frustration, excitement)",
        "Reflective": "Meta-memory (Logs of how the system synthesizes information)"
    }

    output = ["Brain OS Five-Sector Ontology:\n"]
    for sector, description in sectors.items():
        output.append(f"- {sector}: {description}")

    return "\n".join(output)


@mcp.tool
async def get_all_memories(
    limit: int = Field(default=50, description="Maximum number of memories to return", ge=1, le=200),
) -> str:
    """
    Retrieve all memories from the Synaptic Graph.

    Returns all active bubbles ordered by recency (most recent first).
    Use this to get a complete overview of stored memories.
    """
    try:
        # Lazy imports
        _, _, get_all_bubbles = _get_queries()

        results = await get_all_bubbles(limit)

        if not results:
            return "No memories stored yet. Use create_memory to store your first memory."

        # Group by sector for summary
        sector_counts = {}
        for bubble in results:
            sector_counts[bubble.sector] = sector_counts.get(bubble.sector, 0) + 1

        output = [
            f"📊 Total Memories: {len(results)}\n",
            f"📈 Sector Distribution:\n"
        ]
        for sector, count in sorted(sector_counts.items()):
            percentage = (count / len(results)) * 100
            bar = "█" * int(percentage / 5)
            output.append(f"  {sector:12} │ {bar} {count} ({percentage:.1f}%)\n")

        output.append(f"\n{'─' * 60}\n")
        output.append("Recent Memories:\n\n")

        for i, bubble in enumerate(results, 1):
            output.append(
                f"{i}. [{bubble.sector}] Salience: {bubble.salience:.2f}\n"
                f"   Created: {bubble.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"   Content: {bubble.content[:100]}{'...' if len(bubble.content) > 100 else ''}\n"
            )

        return "\n".join(output)
    except Exception as e:
        logger.error(f"Failed to retrieve all memories: {e}")
        return f"Error retrieving memories: {str(e)}"


@mcp.tool
async def visualize_memories(
    limit: int = Field(default=50, description="Maximum number of memories to visualize", ge=1, le=200),
) -> str:
    """
    Generate a visual chart of memory distribution and statistics.

    Creates ASCII-based charts showing sector distribution, salience spread,
    and temporal patterns of stored memories.
    """
    try:
        _, _, get_all_bubbles = _get_queries()
        results = await get_all_bubbles(limit)

        if not results:
            return "No memories to visualize. Store some memories first!"

        # Calculate statistics
        sector_counts = {}
        salience_by_sector = {}
        total_salience = 0

        for bubble in results:
            sector_counts[bubble.sector] = sector_counts.get(bubble.sector, 0) + 1
            if bubble.sector not in salience_by_sector:
                salience_by_sector[bubble.sector] = []
            salience_by_sector[bubble.sector].append(bubble.salience)
            total_salience += bubble.salience

        avg_salience = total_salience / len(results) if results else 0

        # Build visualization
        output = ["\n" + "=" * 60 + "\n"]
        output.append("🧠 BRAIN OS MEMORY VISUALIZATION\n")
        output.append("=" * 60 + "\n\n")

        # Summary stats
        output.append(f"📊 Summary Statistics\n")
        output.append(f"   Total Memories: {len(results)}\n")
        output.append(f"   Average Salience: {avg_salience:.2f}\n")
        output.append(f"   Sectors Active: {len(sector_counts)}/5\n\n")

        # Sector distribution bar chart
        output.append(f"📈 Sector Distribution\n")
        max_count = max(sector_counts.values()) if sector_counts else 1

        for sector in ["Episodic", "Semantic", "Procedural", "Emotional", "Reflective"]:
            count = sector_counts.get(sector, 0)
            if count > 0:
                bar_length = int((count / max_count) * 30)
                bar = "█" * bar_length
                avg_sec_salience = sum(salience_by_sector[sector]) / len(salience_by_sector[sector])
                output.append(f"   {sector:12} │ {bar} {count} (avg salience: {avg_sec_salience:.2f})\n")
            else:
                output.append(f"   {sector:12} │ (empty)\n")

        # Salience distribution histogram
        output.append(f"\n📉 Salience Distribution\n")
        salience_bins = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
        for bubble in results:
            s = bubble.salience
            if s < 0.2:
                salience_bins["0.0-0.2"] += 1
            elif s < 0.4:
                salience_bins["0.2-0.4"] += 1
            elif s < 0.6:
                salience_bins["0.4-0.6"] += 1
            elif s < 0.8:
                salience_bins["0.6-0.8"] += 1
            else:
                salience_bins["0.8-1.0"] += 1

        max_bin = max(salience_bins.values()) if salience_bins else 1
        for label, count in salience_bins.items():
            if count > 0:
                bar_length = int((count / max_bin) * 20)
                bar = "▓" * bar_length
                output.append(f"   {label:8} │ {bar} {count}\n")

        # Time distribution (by date)
        output.append(f"\n📅 Recent Activity (Last 7 Days)\n")
        from datetime import timedelta

        date_counts = {}
        now = datetime.now(timezone.utc)
        for bubble in results:
            days_ago = (now - bubble.created_at).days
            if days_ago < 7:
                date_str = bubble.created_at.strftime("%Y-%m-%d")
                date_counts[date_str] = date_counts.get(date_str, 0) + 1

        if date_counts:
            max_day = max(date_counts.values())
            for date_str in sorted(date_counts.keys(), reverse=True)[:7]:
                count = date_counts[date_str]
                bar_length = int((count / max_day) * 15)
                bar = "●" * bar_length
                output.append(f"   {date_str} │ {bar} {count}\n")
        else:
            output.append(f"   (No activity in the last 7 days)\n")

        output.append("\n" + "=" * 60 + "\n")

        return "\n".join(output)
    except Exception as e:
        logger.error(f"Failed to visualize memories: {e}")
        return f"Error visualizing memories: {str(e)}"
