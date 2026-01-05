"""
Simple Remote Brain OS MCP Client using direct HTTP requests
No complex dependencies required - uses Python's built-in libraries plus requests.
"""

import json
import requests
from typing import Dict, Any, List

# Remote Brain OS MCP server URL
REMOTE_MCP_URL = "https://brainoz.worfklow.org/mcp"


class SimpleBrainOSClient:
    """Simple client for interacting with remote Brain OS MCP server via HTTP."""

    def __init__(self, url: str = REMOTE_MCP_URL):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Make a JSON-RPC style request to the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }

        try:
            response = self.session.post(
                self.url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                return f"Error: {result['error']}"

            return result.get('result', result)

        except requests.exceptions.RequestException as e:
            return f"Connection error: {e}"
        except json.JSONDecodeError as e:
            return f"JSON decode error: {e}"

    def test_connection(self) -> bool:
        """Test if we can connect to the server."""
        try:
            response = self.session.get(
                self.url.replace('/mcp', '/health'),
                timeout=10
            )
            if response.status_code == 200:
                print(f"✓ Connected to {self.url}")
                print(f"✓ Health check: {response.json()}")
                return True
            else:
                print(f"✗ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def list_tools(self) -> str:
        """List all available tools from the remote server."""
        result = self._make_request("tools/list")
        if isinstance(result, dict) and 'tools' in result:
            tools = result['tools']
            output = [f"\n{'='*60}"]
            output.append(f"Connected to: {self.url}")
            output.append(f"{'='*60}")
            output.append(f"\nAvailable Tools ({len(tools)}):\n")

            for i, tool in enumerate(tools, 1):
                output.append(f"{i}. {tool.get('name', 'Unknown')}")
                output.append(f"   Description: {tool.get('description', 'No description')}")
                if 'inputSchema' in tool and 'properties' in tool['inputSchema']:
                    output.append("   Parameters:")
                    for param, details in tool['inputSchema']['properties'].items():
                        desc = details.get('description', 'No description')
                        param_type = details.get('type', 'any')
                        output.append(f"     - {param} ({param_type}): {desc}")
                output.append("")

            result_str = "\n".join(output)
            print(result_str)
            return result_str
        else:
            print(f"Unexpected response: {result}")
            return str(result)

    def create_memory(self, content: str, sector: str, source: str = "simple_client", salience: float = 0.5) -> str:
        """Create a new memory in Brain OS."""
        result = self._make_request("tools/call", {
            "name": "create_memory",
            "arguments": {
                "content": content,
                "sector": sector,
                "source": source,
                "salience": salience
            }
        })
        print(f"\n✓ {result}")
        return str(result)

    def get_memory(self, query: str, limit: int = 10) -> str:
        """Search for memories."""
        result = self._make_request("tools/call", {
            "name": "get_memory",
            "arguments": {
                "query": query,
                "limit": limit
            }
        })
        print(f"\n{result}")
        return str(result)

    def get_all_memories(self, limit: int = 50) -> str:
        """Get all memories."""
        result = self._make_request("tools/call", {
            "name": "get_all_memories",
            "arguments": {
                "limit": limit
            }
        })
        print(f"\n{result}")
        return str(result)

    def list_sectors(self) -> str:
        """List all cognitive sectors."""
        result = self._make_request("tools/call", {
            "name": "list_sectors",
            "arguments": {}
        })
        print(f"\n{result}")
        return str(result)

    def visualize_memories(self, limit: int = 50) -> str:
        """Visualize memory distribution."""
        result = self._make_request("tools/call", {
            "name": "visualize_memories",
            "arguments": {
                "limit": limit
            }
        })
        print(f"\n{result}")
        return str(result)


def demo_workflow():
    """Demonstrate Brain OS functionality."""
    client = SimpleBrainOSClient()

    print("\n" + "="*60)
    print("BRAIN OS SIMPLE CLIENT - DEMO WORKFLOW")
    print("="*60)

    # 1. Test connection
    print("\n[1/6] Testing connection...")
    if not client.test_connection():
        print("Cannot proceed without connection. Exiting.")
        return

    # 2. List available tools
    print("\n[2/6] Discovering available tools...")
    client.list_tools()

    # 3. List sectors
    print("\n[3/6] Getting cognitive sectors...")
    client.list_sectors()

    # 4. Create a test memory
    print("\n[4/6] Creating a test memory...")
    client.create_memory(
        content="Testing simple HTTP client connection to Brain OS from Claude Code",
        sector="Episodic",
        source="demo_workflow",
        salience=0.8
    )

    # 5. Search for the memory
    print("\n[5/6] Searching for recent memories...")
    client.get_memory("simple HTTP", limit=5)

    # 6. Visualize memories
    print("\n[6/6] Visualizing memory distribution...")
    client.visualize_memories(limit=100)

    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)


# Create a global client instance for easy access
brainos = SimpleBrainOSClient()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            brainos.test_connection()

        elif command == "demo":
            demo_workflow()

        elif command == "list":
            brainos.list_tools()

        elif command == "sectors":
            brainos.list_sectors()

        elif command == "visualize":
            brainos.visualize_memories()

        elif command == "memories":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            brainos.get_all_memories(limit)

        elif command == "search":
            if len(sys.argv) < 3:
                print("Usage: python3 simple_brainos_client.py search <query>")
            else:
                query = " ".join(sys.argv[2:])
                brainos.get_memory(query)

        elif command == "create":
            if len(sys.argv) < 4:
                print("Usage: python3 simple_brainos_client.py create <sector> <content>")
            else:
                sector = sys.argv[2]
                content = " ".join(sys.argv[3:])
                brainos.create_memory(content, sector)

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
        demo_workflow()
