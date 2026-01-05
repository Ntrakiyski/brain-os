"""
Brain OS Interactive Client for Claude Code
Use this module to interact with your remote Brain OS server.
"""

import json
import subprocess
import sys


class BrainOSInteractive:
    """Interactive client for Brain OS - works around network restrictions."""

    def __init__(self, url: str = "https://brainoz.worfklow.org/mcp"):
        self.url = url

    def _curl_request(self, endpoint: str, data: dict = None) -> str:
        """Make request using curl to bypass Python proxy issues."""
        url = self.url if endpoint == '/mcp' else self.url.replace('/mcp', endpoint)

        if data:
            json_data = json.dumps(data)
            cmd = [
                'curl', '-X', 'POST',
                '-H', 'Content-Type: application/json',
                '-H', 'Accept: application/json',
                '-d', json_data,
                '-s',  # silent
                '--max-time', '30',
                url
            ]
        else:
            cmd = ['curl', '-s', '--max-time', '30', url]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Request timed out"
        except Exception as e:
            return f"Error: {e}"

    def test_connection(self):
        """Test connection to Brain OS server."""
        print("Testing connection to Brain OS...")
        result = self._curl_request('/health')
        print(f"Result: {result}")
        return result

    def list_tools(self):
        """List available tools."""
        print("Fetching available tools...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        result = self._curl_request('/mcp', payload)
        print(result)
        return result

    def create_memory(self, content: str, sector: str, source: str = "interactive", salience: float = 0.5):
        """Create a memory in Brain OS."""
        print(f"Creating memory in sector '{sector}'...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "create_memory",
                "arguments": {
                    "content": content,
                    "sector": sector,
                    "source": source,
                    "salience": salience
                }
            }
        }
        result = self._curl_request('/mcp', payload)
        print(result)
        return result

    def search_memories(self, query: str, limit: int = 10):
        """Search for memories."""
        print(f"Searching for: {query}...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_memory",
                "arguments": {
                    "query": query,
                    "limit": limit
                }
            }
        }
        result = self._curl_request('/mcp', payload)
        print(result)
        return result

    def get_all_memories(self, limit: int = 50):
        """Get all memories."""
        print(f"Fetching all memories (limit: {limit})...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_all_memories",
                "arguments": {
                    "limit": limit
                }
            }
        }
        result = self._curl_request('/mcp', payload)
        print(result)
        return result

    def list_sectors(self):
        """List cognitive sectors."""
        print("Fetching cognitive sectors...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_sectors",
                "arguments": {}
            }
        }
        result = self._curl_request('/mcp', payload)
        print(result)
        return result

    def visualize(self, limit: int = 100):
        """Visualize memory distribution."""
        print("Generating memory visualization...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "visualize_memories",
                "arguments": {
                    "limit": limit
                }
            }
        }
        result = self._curl_request('/mcp', payload)
        print(result)
        return result


# Create global instance
brain = BrainOSInteractive()


# Convenience functions
def test():
    """Test connection to Brain OS."""
    return brain.test_connection()


def tools():
    """List available tools."""
    return brain.list_tools()


def sectors():
    """List cognitive sectors."""
    return brain.list_sectors()


def create(content, sector, salience=0.5):
    """
    Create a new memory.

    Example:
        create("Learned about MCP integration", "Semantic", 0.8)
    """
    return brain.create_memory(content, sector, salience=salience)


def search(query, limit=10):
    """
    Search for memories.

    Example:
        search("MCP", 5)
    """
    return brain.search_memories(query, limit)


def memories(limit=50):
    """
    Get all memories.

    Example:
        memories(20)
    """
    return brain.get_all_memories(limit)


def viz(limit=100):
    """
    Visualize memory distribution.

    Example:
        viz()
    """
    return brain.visualize(limit)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "test":
            test()
        elif cmd == "tools":
            tools()
        elif cmd == "sectors":
            sectors()
        elif cmd == "memories":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            memories(limit)
        elif cmd == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            search(query)
        elif cmd == "create" and len(sys.argv) > 3:
            sector = sys.argv[2]
            content = " ".join(sys.argv[3:])
            create(content, sector)
        elif cmd == "viz":
            viz()
        else:
            print("Commands: test, tools, sectors, memories, search <query>, create <sector> <content>, viz")
    else:
        print("\n=== Brain OS Interactive Client ===")
        print("Available functions:")
        print("  test()                          - Test connection")
        print("  tools()                         - List available tools")
        print("  sectors()                       - List cognitive sectors")
        print("  create(content, sector, [sal])  - Create memory")
        print("  search(query, [limit])          - Search memories")
        print("  memories([limit])               - Get all memories")
        print("  viz([limit])                    - Visualize distribution")
        print("\nExample usage:")
        print('  >>> from brainos_interactive import *')
        print('  >>> test()')
        print('  >>> create("Testing MCP integration", "Episodic", 0.8)')
        print('  >>> search("MCP")')
