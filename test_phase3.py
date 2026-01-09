"""
Test client for Brain OS Phase 3 tools.
Tests the new instinctive memory, contextual retrieval, and visualization tools.
"""

import asyncio
import os
from fastmcp import Client

# Configuration
MCP_URL = "http://127.0.0.1:9131/mcp"

async def test_phase3_tools():
    """Test all Phase 3 tools."""

    print("=" * 60)
    print("Brain OS Phase 3 Tool Testing")
    print("=" * 60)
    print(f"Connecting to: {MCP_URL}")
    print()

    async with Client(MCP_URL) as client:
        # Test 1: Create memories with Phase 3 enhanced fields
        print("\n[TEST 1] create_memory with Phase 3 fields")
        print("-" * 60)

        result = await client.call_tool("create_memory", {
            "content": "Project A uses FastAPI for the backend API framework",
            "sector": "Semantic",
            "source": "technical_decision",
            "salience": 0.8,
            "memory_type": "instinctive",
            "activation_threshold": 0.2,
            "entities": ["Project A", "FastAPI", "API", "backend"],
            "observations": [
                "Chosen over Flask for async support",
                "Automatic OpenAPI documentation",
                "Native Pydantic validation"
            ]
        })
        print(result)

        result = await client.call_tool("create_memory", {
            "content": "Project A chose PostgreSQL over MongoDB for ACID compliance",
            "sector": "Semantic",
            "source": "technical_decision",
            "salience": 0.7,
            "memory_type": "instinctive",
            "entities": ["Project A", "PostgreSQL", "MongoDB", "database"],
            "observations": ["Complex transactions", "Financial data integrity"]
        })

        result = await client.call_tool("create_memory", {
            "content": "Project A uses Redis for session caching with 30-minute TTL",
            "sector": "Procedural",
            "source": "technical_decision",
            "salience": 0.6,
            "memory_type": "instinctive",
            "entities": ["Project A", "Redis", "cache", "sessions"],
            "observations": ["Persistent caching", "Fast access"]
        })

        result = await client.call_tool("create_memory", {
            "content": "Discussing API design patterns with the team on Tuesday",
            "sector": "Episodic",
            "source": "meeting",
            "salience": 0.5,
            "memory_type": "thinking",
            "entities": ["API", "design", "team", "meeting"]
        })

        # Wait a moment for data to persist
        await asyncio.sleep(1)

        # Test 2: get_instinctive_memory (automatic activation)
        print("\n[TEST 2] get_instinctive_memory (Oven Analogy)")
        print("-" * 60)
        print("Input: 'I'm starting work on Project A again'")

        result = await client.call_tool("get_instinctive_memory", {
            "user_input": "I'm starting work on Project A again"
        })
        print(result)

        # Test 3: get_memory_relations (contextual retrieval)
        print("\n[TEST 3] get_memory_relations (3-Agent System)")
        print("-" * 60)
        print("Query: 'Why did I choose PostgreSQL for Project A?'")

        result = await client.call_tool("get_memory_relations", {
            "query": "Why did I choose PostgreSQL for Project A?",
            "conversation_history": [
                "What database should I use?",
                "I'm considering PostgreSQL vs MongoDB",
                "What about transaction support?"
            ]
        })
        print(result)

        # Test 4: get_all_memories to see what we have
        print("\n[TEST 4] get_all_memories (Phase 3 fields)")
        print("-" * 60)

        result = await client.call_tool("get_all_memories", {
            "limit": 10
        })
        print(result)

        # Test 5: visualize_relations
        print("\n[TEST 5] visualize_relations (Mermaid + Neo4j Browser)")
        print("-" * 60)
        print("Note: This requires a valid bubble ID from get_all_memories")

        # For now, just show the help message since we don't have IDs yet
        result = await client.call_tool("visualize_relations", {
            "bubble_id": "999",  # Invalid ID to show error message
            "depth": 2
        })
        print(result)

    print("\n" + "=" * 60)
    print("Phase 3 Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_phase3_tools())
