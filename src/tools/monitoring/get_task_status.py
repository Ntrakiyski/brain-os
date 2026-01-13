"""
Task Status Query Tool.

Phase 4: Query background task status.
"""

import logging

from pydantic import Field

from src.tasks.background import get_all_task_status, get_task_status_by_name

logger = logging.getLogger(__name__)


def register_get_task_status(mcp) -> None:
    """Register the get_task_status tool with FastMCP."""

    @mcp.tool
    async def get_task_status(
        task_name: str = Field(
            default="all",
            description="Task name or 'all' for all tasks. Available: synaptic_pruning, cloud_synthesis, health_check"
        )
    ) -> str:
        """
        Query status of background tasks.

        **Use this to check when background maintenance tasks will run.**

        Background Tasks:
        - **synaptic_pruning**: Daily (every 24 hours) - Decays salience of unused memories
        - **cloud_synthesis**: Weekly (every 168 hours) - Generates Reflective insights
        - **health_check**: Hourly (every 1 hour) - Monitors system health

        When to Use This:
        ✓ Checking if maintenance is scheduled
        ✓ Troubleshooting automated tasks
        ✓ Verifying background task configuration

        **Example:**
        ```
        get_task_status()  # Get all tasks
        get_task_status(task_name="synaptic_pruning")  # Get specific task
        ```
        """
        logger.info(f"Querying task status: {task_name}")

        if task_name == "all":
            tasks = await get_all_task_status()
            return format_all_tasks_report(tasks)
        else:
            task = await get_task_status_by_name(task_name)
            return format_single_task_report(task)


def format_all_tasks_report(tasks: list) -> str:
    """Format all tasks report."""
    lines = []
    lines.append("## Background Task Status")
    lines.append("")

    for task in tasks:
        lines.append(f"### {task['name']}")
        lines.append(f"**Status**: {task['status']}")
        lines.append(f"**Schedule**: Every {task['interval']}")
        lines.append(f"**Last Run**: {task['last_run']}")
        lines.append(f"**Next Run**: {task['next_run']}")
        lines.append(f"**Description**: {task['description']}")
        lines.append("")

    lines.append("**Notes:**")
    lines.append("- Tasks run automatically in the background")
    lines.append("- Synaptic pruning reduces salience of memories not accessed in 30+ days")
    lines.append("- Cloud synthesis generates Reflective insights from memory clusters")
    lines.append("- Health check monitors Neo4j and LLM API availability")

    return "\n".join(lines)


def format_single_task_report(task: dict) -> str:
    """Format single task report."""
    if task.get("error"):
        return f"## Task Not Found\n\nError: {task['error']}"

    lines = []
    lines.append(f"## Background Task: {task['name']}")
    lines.append("")
    lines.append(f"**Status**: {task['status']}")
    lines.append(f"**Schedule**: Every {task['interval']}")
    lines.append(f"**Last Run**: {task['last_run']}")
    lines.append(f"**Next Run**: {task['next_run']}")
    lines.append("")
    lines.append(f"**Description**: {task['description']}")

    if task.get("last_run") and task["last_run"] != "Never":
        lines.append("")
        lines.append("**Recent History:**")
        lines.append(f"  Last run completed successfully")

    return "\n".join(lines)
