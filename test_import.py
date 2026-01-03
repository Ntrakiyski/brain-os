"""Test script to debug import issues"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    print("Testing imports...", file=sys.stderr)
    try:
        print("1. Importing fastmcp...", file=sys.stderr)
        from fastmcp import FastMCP
        print("   ✓ fastmcp imported", file=sys.stderr)
    except Exception as e:
        print(f"   ✗ fastmcp failed: {e}", file=sys.stderr)
        raise

    try:
        print("2. Importing config...", file=sys.stderr)
        from src.core.config import neo4j
        print(f"   ✓ config imported, neo4j uri: {neo4j.uri}", file=sys.stderr)
    except Exception as e:
        print(f"   ✗ config failed: {e}", file=sys.stderr)
        raise

    try:
        print("3. Importing schemas...", file=sys.stderr)
        from src.utils.schemas import BubbleCreate
        print("   ✓ schemas imported", file=sys.stderr)
    except Exception as e:
        print(f"   ✗ schemas failed: {e}", file=sys.stderr)
        raise

    try:
        print("4. Importing connection...", file=sys.stderr)
        from src.database import connection
        print("   ✓ connection imported", file=sys.stderr)
    except Exception as e:
        print(f"   ✗ connection failed: {e}", file=sys.stderr)
        raise

    try:
        print("5. Importing queries...", file=sys.stderr)
        from src.database.queries import upsert_bubble, search_bubbles
        print("   ✓ queries imported", file=sys.stderr)
    except Exception as e:
        print(f"   ✗ queries failed: {e}", file=sys.stderr)
        raise

    try:
        print("6. Importing memory_tools...", file=sys.stderr)
        from src.tools.memory_tools import mcp
        print("   ✓ memory_tools imported", file=sys.stderr)
    except Exception as e:
        print(f"   ✗ memory_tools failed: {e}", file=sys.stderr)
        raise

    print("\nAll imports successful!", file=sys.stderr)

if __name__ == "__main__":
    test_imports()
