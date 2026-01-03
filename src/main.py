"""
Brain OS - Cognitive Operating System
Main entry point for the MCP server.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP

from src.tools.memory_tools import mcp
from src.database.connection import get_connection, close_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    """Manage application lifecycle - connect to Neo4j on startup."""
    try:
        logger.info("Starting Brain OS MCP server...")
        await get_connection()
        logger.info("Neo4j connection established")
        yield
    finally:
        logger.info("Shutting down Brain OS MCP server...")
        await close_connection()
        logger.info("Neo4j connection closed")


# Create the main MCP instance with lifespan
# Export the mcp instance for FastMCP CLI
__all__ = ["mcp"]
