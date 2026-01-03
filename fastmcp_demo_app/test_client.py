import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8000/mcp")

async def test_tools():
    async with client:
        # Test greet tool
        result = await client.call_tool("greet", {"name": "Claude"})
        print("greet('Claude'):", result)

        # Test add tool
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print("add(5, 3):", result)

        # Test get_weather tool
        result = await client.call_tool("get_weather", {"city": "Tokyo"})
        print("get_weather('Tokyo'):", result)

asyncio.run(test_tools())
