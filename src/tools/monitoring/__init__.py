"""
Monitoring tools for Brain OS.

Phase 4: System health checks and task status queries.
"""

from fastmcp import FastMCP

from src.tools.monitoring.get_system_health import register_get_system_health
from src.tools.monitoring.get_task_status import register_get_task_status


def register_monitoring_tools(mcp: FastMCP) -> None:
    """Register all monitoring tools with the MCP server."""
    register_get_system_health(mcp)
    register_get_task_status(mcp)
