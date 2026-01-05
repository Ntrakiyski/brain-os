"""
Remote Brain OS MCP Client
Connect to deployed Brain OS server and interact with it.
"""

import asyncio
from fastmcp import Client
from typing import Optional

# Remote Brain OS MCP server URL
REMOTE_MCP_URL = "https://brainoz.worfklow.org/mcp"

class BrainOSClient:
    """Client for interacting with remote Brain OS MCP server."""

    def __init__(self, url: str = REMOTE_MCP_URL):
        self.url = url
        self.client = Client(url)

    async def list_tools(self):
        """List all available tools from the remote server."""
        async with self.client:
            tools = await self.client.list_tools()
            print(f"\n{'='*60}")
            print(f"Connected to: {self.url}")
            print(f"{'='*60}")
            print(f"\nAvailable Tools ({len(tools)}):\n")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name}")
                print(f"   Description: {tool.description}")
                if tool.inputSchema and 'properties' in tool.inputSchema:
                    print(f"   Parameters:")
                    for param, details in tool.inputSchema['properties'].items():
                        desc = details.get('description', 'No description')
                        param_type = details.get('type', 'any')
                        print(f"     - {param} ({param_type}): {desc}")
                print()
            return tools

    async def create_memory(self, content: str, sector: str, source: str = "remote_client", salience: float = 0.5):
        """Create a new memory in Brain OS."""
        async with self.client:
            result = await self.client.call_tool("create_memory", {
                "content": content,
                "sector": sector,
                "source": source,
                "salience": salience
            })
            print(f"\n✓ {result}")
            return result

    async def get_memory(self, query: str, limit: int = 10):
        """Search for memories."""
        async with self.client:
            result = await self.client.call_tool("get_memory", {
                "query": query,
                "limit": limit
            })
            print(f"\n{result}")
            return result

    async def get_all_memories(self, limit: int = 50):
        """Get all memories."""
        async with self.client:
            result = await self.client.call_tool("get_all_memories", {
                "limit": limit
            })
            print(f"\n{result}")
            return result

    async def list_sectors(self):
        """List all cognitive sectors."""
        async with self.client:
            result = await self.client.call_tool("list_sectors", {})
            print(f"\n{result}")
            return result

    async def visualize_memories(self, limit: int = 50):
        """Visualize memory distribution."""
        async with self.client:
            result = await self.client.call_tool("visualize_memories", {
                "limit": limit
            })
            print(f"\n{result}")
            return result


# Convenience functions for direct use
async def test_connection():
    """Test connection to remote Brain OS server."""
    client = BrainOSClient()
    try:
        await client.list_tools()
        print("✓ Connection successful!")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


async def demo_workflow():
    """Demonstrate Brain OS functionality."""
    client = BrainOSClient()

    print("\n" + "="*60)
    print("BRAIN OS REMOTE CLIENT - DEMO WORKFLOW")
    print("="*60)

    # 1. List available tools
    print("\n[1/5] Discovering available tools...")
    await client.list_tools()

    # 2. List sectors
    print("\n[2/5] Getting cognitive sectors...")
    await client.list_sectors()

    # 3. Create a test memory
    print("\n[3/5] Creating a test memory...")
    await client.create_memory(
        content="Testing remote MCP connection from Claude Code",
        sector="Episodic",
        source="demo_workflow",
        salience=0.8
    )

    # 4. Search for the memory
    print("\n[4/5] Searching for recent memories...")
    await client.get_memory("remote MCP", limit=5)

    # 5. Visualize memories
    print("\n[5/5] Visualizing memory distribution...")
    await client.visualize_memories(limit=100)

    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)


# Create a global client instance for easy access
brainos = BrainOSClient()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            asyncio.run(test_connection())

        elif command == "demo":
            asyncio.run(demo_workflow())

        elif command == "list":
            asyncio.run(brainos.list_tools())

        elif command == "sectors":
            asyncio.run(brainos.list_sectors())

        elif command == "visualize":
            asyncio.run(brainos.visualize_memories())

        elif command == "memories":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            asyncio.run(brainos.get_all_memories(limit))

        elif command == "search":
            if len(sys.argv) < 3:
                print("Usage: python remote_brainos_client.py search <query>")
            else:
                query = " ".join(sys.argv[2:])
                asyncio.run(brainos.get_memory(query))

        elif command == "create":
            if len(sys.argv) < 4:
                print("Usage: python remote_brainos_client.py create <sector> <content>")
            else:
                sector = sys.argv[2]
                content = " ".join(sys.argv[3:])
                asyncio.run(brainos.create_memory(content, sector))

        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  test      - Test connection")
            print("  demo      - Run full demo workflow")
            print("  list      - List available tools")
            print("  sectors   - List cognitive sectors")
            print("  visualize - Visualize memory distribution")
            print("  memories  - Get all memories")
            print("  search <query> - Search for memories")
            print("  create <sector> <content> - Create a new memory")
    else:
        # Default: run demo
        asyncio.run(demo_workflow())
