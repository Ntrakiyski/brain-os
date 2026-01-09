"""
Memory visualization tool.
Generates ASCII-based charts and statistics.
"""

import logging
from datetime import datetime, timezone
from pydantic import Field

from src.database.queries.memory import get_all_bubbles

logger = logging.getLogger(__name__)


def register_visualize_memory(mcp) -> None:
    """Register the memory visualization tool with FastMCP."""

    @mcp.tool
    async def visualize_memories(
        limit: int = Field(
            default=50, description="Maximum number of memories to visualize", ge=1, le=200
        ),
    ) -> str:
        """
        Generate a visual chart of memory distribution and statistics.

        Creates ASCII-based charts showing sector distribution, salience spread,
        and temporal patterns of stored memories.
        """
        try:
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
                    avg_sec_salience = sum(salience_by_sector[sector]) / len(
                        salience_by_sector[sector]
                    )
                    output.append(
                        f"   {sector:12} │ {bar} {count} (avg salience: {avg_sec_salience:.2f})\n"
                    )
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
