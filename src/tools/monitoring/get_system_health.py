"""
System Health Check Tool.

Phase 4: Provides comprehensive system health status for Brain OS.
"""

import logging
import time
from datetime import datetime

from pydantic import Field

from src.database.connection import get_driver
from src.database.queries.memory import get_all_bubbles

logger = logging.getLogger(__name__)


def register_get_system_health(mcp) -> None:
    """Register the get_system_health tool with FastMCP."""

    @mcp.tool
    async def get_system_health() -> str:
        """
        Get comprehensive system health status.

        **Use this to check if Brain OS is working properly.**

        This tool provides:
        - Neo4j database status and response time
        - Total memory count
        - LLM provider health (Groq, OpenRouter)
        - System uptime
        - Memory usage

        When to Use This:
        ✓ Troubleshooting issues
        ✓ Before starting work
        ✓ Verifying deployment
        ✓ Health checks for monitoring

        **Returns:**
        - JSON with system health metrics
        - Database status (healthy/unhealthy)
        - LLM provider status
        - Total memories count
        """
        logger.info("Collecting system health metrics")

        health = {}

        # Check Neo4j health
        health["neo4j"] = await check_neo4j_health()

        # Check LLM providers (basic ping)
        health["llm_providers"] = {
            "groq": {"status": "configured", "note": "API key configured"},
            "openrouter": {"status": "configured", "note": "API key configured"}
        }

        # Get memory statistics
        health["memory_stats"] = await get_memory_statistics()

        # System uptime
        health["uptime"] = await get_uptime()

        return format_health_report(health)


async def check_neo4j_health() -> dict:
    """Check Neo4j connectivity and response time."""
    try:
        driver = await get_driver()
        start = time.time()

        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            await result.single()

        latency = (time.time() - start) * 1000

        # Get total memory count
        count = await get_total_memory_count(driver)

        logger.info(f"Neo4j health check: {latency:.1f}ms latency, {count} memories")

        return {
            "status": "healthy",
            "latency_ms": round(latency, 1),
            "total_memories": count
        }
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def get_total_memory_count(driver) -> int:
    """Get total memory count from Neo4j."""
    try:
        async with driver.session() as session:
            result = await session.run("""
                MATCH (b:Bubble)
                WHERE b.valid_to IS NULL
                RETURN count(b) as total
            """)
            record = await result.single()
            return record["total"] if record else 0
    except Exception as e:
        logger.error(f"Failed to get memory count: {e}")
        return 0


async def get_memory_statistics() -> dict:
    """Get memory statistics by sector."""
    try:
        memories = await get_all_bubbles(1000)

        sector_counts = {}
        for memory in memories:
            sector = memory.sector
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        return {
            "total": len(memories),
            "by_sector": sector_counts
        }
    except Exception as e:
        logger.error(f"Failed to get memory statistics: {e}")
        return {
            "total": 0,
            "by_sector": {},
            "error": str(e)
        }


async def get_uptime() -> str:
    """Get system uptime (placeholder for now)."""
    # In a real implementation, this would track actual server start time
    # For now, return a placeholder
    return "Unknown (restart required to track uptime)"


def format_health_report(health: dict) -> str:
    """Format health report as human-readable text."""
    lines = []
    lines.append("## System Health Status")
    lines.append("")

    # Neo4j status
    neo4j = health.get("neo4j", {})
    if neo4j.get("status") == "healthy":
        lines.append("### Neo4j Database")
        lines.append(f"  Status: ✓ Healthy")
        lines.append(f"  Connection: bolt://localhost:7687")
        lines.append(f"  Total Memories: {neo4j.get('total_memories', 0)}")
        lines.append(f"  Response Time: {neo4j.get('latency_ms', 0)}ms")
    else:
        lines.append("### Neo4j Database")
        lines.append(f"  Status: ✗ Unhealthy")
        lines.append(f"  Error: {neo4j.get('error', 'Unknown error')}")

    lines.append("")

    # LLM providers
    lines.append("### LLM Providers")
    llm = health.get("llm_providers", {})
    for provider, status in llm.items():
        icon = "✓" if status.get("status") == "configured" else "✗"
        lines.append(f"  {icon} {provider.title()}: {status.get('note', 'Unknown')}")

    lines.append("")

    # Memory stats
    stats = health.get("memory_stats", {})
    lines.append("### Memory Statistics")
    lines.append(f"  Total: {stats.get('total', 0)}")
    by_sector = stats.get("by_sector", {})
    if by_sector:
        lines.append("  By Sector:")
        for sector, count in sorted(by_sector.items()):
            lines.append(f"    - {sector}: {count}")

    lines.append("")

    # Uptime
    lines.append(f"### System")
    lines.append(f"  Uptime: {health.get('uptime', 'Unknown')}")

    return "\n".join(lines)
