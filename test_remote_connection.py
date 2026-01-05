#!/usr/bin/env python3
"""
Quick test script to verify Brain OS remote MCP connection.
Run this from your local machine to test the deployed server.
"""

import sys
import json

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found.")
    print("Install it with: pip install requests")
    sys.exit(1)

BRAIN_OS_URL = "https://brainoz.worfklow.org/mcp"
HEALTH_URL = "https://brainoz.worfklow.org/health"


def test_health():
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Health check PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check FAILED: {e}")
        return False


def test_tools_list():
    """Test listing MCP tools."""
    print("\n🔍 Testing tools list...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        response = requests.post(
            BRAIN_OS_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'tools' in result['result']:
                tools = result['result']['tools']
                print(f"✅ Tools list PASSED - Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool.get('description', 'No description')}")
                return True
            else:
                print(f"❌ Tools list FAILED: Unexpected response format")
                print(f"   Response: {result}")
                return False
        else:
            print(f"❌ Tools list FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools list FAILED: {e}")
        return False


def test_create_memory():
    """Test creating a memory."""
    print("\n🔍 Testing create_memory tool...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "create_memory",
                "arguments": {
                    "content": "Test memory from connection verification script",
                    "sector": "Episodic",
                    "source": "test_script",
                    "salience": 0.5
                }
            }
        }
        response = requests.post(
            BRAIN_OS_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ create_memory PASSED")
            print(f"   Result: {result.get('result', result)}")
            return True
        else:
            print(f"❌ create_memory FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ create_memory FAILED: {e}")
        return False


def test_search_memory():
    """Test searching for memories."""
    print("\n🔍 Testing get_memory tool...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_memory",
                "arguments": {
                    "query": "test",
                    "limit": 5
                }
            }
        }
        response = requests.post(
            BRAIN_OS_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ get_memory PASSED")
            print(f"   Result: {result.get('result', result)[:200]}...")
            return True
        else:
            print(f"❌ get_memory FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ get_memory FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("BRAIN OS REMOTE MCP CONNECTION TEST")
    print("=" * 60)
    print(f"Testing server: {BRAIN_OS_URL}")
    print()

    tests = [
        ("Health Check", test_health),
        ("Tools List", test_tools_list),
        ("Create Memory", test_create_memory),
        ("Search Memory", test_search_memory),
    ]

    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"❌ {name} CRASHED: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests PASSED! Your Brain OS MCP server is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
