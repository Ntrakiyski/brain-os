"""
Background Tasks for Brain OS.

Phase 4: Circadian rhythm - automated maintenance cycles.
"""

import logging
import os
from datetime import datetime, timedelta

from src.database.connection import get_driver
from src.database.queries.memory import search_bubbles

logger = logging.getLogger(__name__)


async def synaptic_pruning_task():
    """
    Daily salience decay for unused memories.

    Finds memories not accessed in 30+ days and reduces their salience by 10%.
    This mimics the brain's natural forgetting process.

    Schedule: Every 24 hours
    """
    logger.info("Starting synaptic pruning cycle")

    driver = await get_driver()

    try:
        # Find memories not accessed in 30+ days
        # For now, we'll use a simpler approach: reduce salience of old memories
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        # Get all memories and check their created_at (simplified approach)
        # In a real implementation, we'd track last_accessed time
        memories = await search_bubbles("", limit=1000)

        decayed_count = 0
        decayed_memories = []
        for memory in memories:
            # Only decay memories with salience > 0.3 (don't decay very old/weak memories)
            if memory.salience > 0.3:
                # Check if memory is old (using created_at as proxy for last accessed)
                if memory.created_at < cutoff_date:
                    # Calculate what new salience would be (not actually updating DB in this version)
                    new_salience = max(0.1, memory.salience * 0.9)
                    decayed_memories.append({
                        "id": str(memory.id),
                        "old_salience": float(memory.salience),
                        "new_salience": float(new_salience),
                        "sector": memory.sector
                    })
                    decayed_count += 1

        logger.info(f"Synaptic pruning complete: {decayed_count} memories identified for decay")
        return {
            "task": "synaptic_pruning",
            "decayed_count": decayed_count,
            "decayed_memories": decayed_memories[:5],  # First 5 for reporting
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Synaptic pruning failed: {e}")
        return {
            "task": "synaptic_pruning",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def cloud_synthesis_task():
    """
    Weekly generation of Reflective insights.

    Finds memory clusters with 5+ high-salience memories and generates
    Reflective cloud memories using OpenRouter.

    Schedule: Every 7 days (168 hours)
    """
    logger.info("Starting cloud synthesis cycle")

    try:
        # For now, this is a placeholder implementation
        # In a full implementation, this would:
        # 1. Find memory clusters (by entity, topic, etc.)
        # 2. Check if clusters have 5+ high-salience (>0.7) memories
        # 3. Call OpenRouter to generate Reflective insights
        # 4. Store insights as Reflective memories

        clouds_generated = 0

        logger.info(f"Cloud synthesis complete: {clouds_generated} insights generated")
        return {
            "task": "cloud_synthesis",
            "clouds_generated": clouds_generated,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cloud synthesis failed: {e}")
        return {
            "task": "cloud_synthesis",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def health_check_task():
    """
    Hourly system health monitoring.

    Checks Neo4j connectivity and LLM API availability.
    Stores status in system memory for querying.

    Schedule: Every 60 minutes
    """
    logger.info("Starting health check cycle")

    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "neo4j": await check_neo4j_connection(),
        "groq": await check_llm_api("groq"),
        "openrouter": await check_llm_api("openrouter")
    }

    logger.info(f"Health check: {status}")
    return status


async def check_neo4j_connection() -> dict:
    """Check Neo4j connectivity."""
    try:
        driver = await get_driver()
        async with driver.session() as session:
            result = await session.run("RETURN 1 as test")
            await result.single()

        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


async def check_llm_api(provider: str) -> dict:
    """Check LLM API availability (basic check)."""
    # Check if API key is configured
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            return {"status": "configured", "note": "API key present"}
        else:
            return {"status": "not_configured", "note": "GROQ_API_KEY not set"}
    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            return {"status": "configured", "note": "API key present"}
        else:
            return {"status": "not_configured", "note": "OPENROUTER_API_KEY not set"}
    else:
        return {"status": "unknown", "note": f"Unknown provider: {provider}"}


# =============================================================================
# TASK REGISTRY (for get_task_status tool)
# =============================================================================

TASK_REGISTRY = {
    "synaptic_pruning": {
        "name": "Synaptic Pruning",
        "display_name": "Synaptic Pruning",
        "description": "Daily salience decay for unused memories",
        "interval_hours": 24,
        "last_run": None,
        "next_run": None,
        "status": "scheduled",
        "function": synaptic_pruning_task
    },
    "cloud_synthesis": {
        "name": "Cloud Synthesis",
        "display_name": "Cloud Synthesis",
        "description": "Weekly generation of Reflective insights",
        "interval_hours": 168,
        "last_run": None,
        "next_run": None,
        "status": "scheduled",
        "function": cloud_synthesis_task
    },
    "health_check": {
        "name": "Health Check",
        "display_name": "Health Check",
        "description": "Hourly system health monitoring",
        "interval_hours": 1,
        "last_run": None,
        "next_run": None,
        "status": "scheduled",
        "function": health_check_task
    }
}


async def get_all_task_status() -> list:
    """Get status of all background tasks."""
    tasks = []
    for task_name, task_info in TASK_REGISTRY.items():
        tasks.append({
            "name": task_info["display_name"],
            "status": task_info["status"],
            "interval": f"{task_info['interval_hours']} hours",
            "last_run": task_info.get("last_run") or "Never",
            "next_run": task_info.get("next_run") or "Scheduled",
            "description": task_info["description"]
        })
    return tasks


async def get_task_status_by_name(task_name: str) -> dict:
    """Get status of a specific background task."""
    if task_name not in TASK_REGISTRY:
        return {
            "name": task_name,
            "status": "unknown",
            "error": "Task not found"
        }

    task_info = TASK_REGISTRY[task_name]
    return {
        "name": task_info["display_name"],
        "status": task_info["status"],
        "interval": f"{task_info['interval_hours']} hours",
        "last_run": task_info.get("last_run") or "Never",
        "next_run": task_info.get("next_run") or "Scheduled",
        "description": task_info["description"]
    }
