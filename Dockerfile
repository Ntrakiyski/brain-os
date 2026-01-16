# BrainOS MCP Server - Optimized for HTTPS/Proxy (Coolify compatible)
# Based on chrome-mcp pattern that works with HTTPS termination

FROM python:3.14-slim

WORKDIR /app

# Install pip packages
RUN pip install --no-cache-dir --upgrade pip

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using pip (simpler, more compatible with proxies)
RUN pip install --no-cache-dir fastmcp>=2.14.2 neo4j>=5.25.0 python-dotenv>=1.0.0 pydantic>=2.10.0 groq>=0.11.0 openai>=1.57.0 pocketflow>=0.0.3 httpx>=0.27.0 arize-phoenix-otel>=0.1.0

# Copy the entire project
COPY . .

# Expose the HTTP MCP port
EXPOSE 9131

# Set environment variables
ENV MCP_PORT=9131
ENV PYTHONUNBUFFERED=1

# Run the MCP server directly via Python (like chrome-mcp - more compatible with HTTPS)
CMD ["python", "brainos_server.py"]
