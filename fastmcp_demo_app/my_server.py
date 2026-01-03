from fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("Demo MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool
def get_weather(city: str) -> str:
    """Get a mock weather report for a city."""
    weather_data = {
        "Tokyo": "Sunny, 22°C",
        "London": "Cloudy, 15°C",
        "New York": "Rainy, 18°C",
        "Paris": "Partly cloudy, 20°C",
    }
    return weather_data.get(city, f"Weather data not available for {city}")

if __name__ == "__main__":
    mcp.run()
