"""
Brain OS MCP Server Entry Point
Wrapper script to handle Python path correctly for Claude Desktop.
"""

import sys
from pathlib import Path

# Add project root to Python path BEFORE any imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can safely import
from src.tools.memory_tools import mcp

if __name__ == "__main__":
    # Run the server
    import asyncio

    # Just import mcp to register tools
    print("Brain OS MCP Server starting...", file=sys.stderr)
    print(f"Project root: {project_root}", file=sys.stderr)
    print(f"Python path includes: {project_root}", file=sys.stderr)
