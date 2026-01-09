"""
Brain OS MCP Server
Minimal entry point with modular tool registration.
"""

import logging
import os
import sys
from pathlib import Path

from fastmcp import FastMCP
from starlette.responses import JSONResponse

# Add project root to Python path BEFORE any imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import tool registration functions
from src.tools import register_memory_tools, register_agent_tools

# Create FastMCP instance
mcp = FastMCP("Brain OS")

# Add health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request) -> JSONResponse:
    """Health check endpoint for deployment monitoring."""
    return JSONResponse({"status": "healthy", "service": "brainos-mcp"})

# Register all tool modules
register_memory_tools(mcp)
register_agent_tools(mcp)


# =============================================================================
# SERVER ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Get port from environment or use default
    port = int(os.getenv("MCP_PORT", 9131))
    host = os.getenv("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting Brain OS MCP Server on {host}:{port}...")
    logger.info("Available tools:")
    logger.info("  - create_memory: Store a new memory in the Synaptic Graph")
    logger.info("  - get_memory: Retrieve memories by search query")
    logger.info("  - get_all_memories: Retrieve all memories")
    logger.info("  - list_sectors: List all cognitive sectors")
    logger.info("  - visualize_memories: Generate memory distribution chart")
    logger.info("  - summarize_project: Summarize project memories using AI")
    logger.info(f"Health check: http://{host}:{port}/health")

    # Run the server directly (compatible with Coolify HTTPS termination)
    mcp.run(transport="http", host=host, port=port)
