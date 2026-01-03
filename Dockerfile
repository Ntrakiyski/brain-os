# Multi-stage Dockerfile for BrainOS MCP Server
FROM python:3.14-slim AS builder

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv (creates virtual environment)
RUN uv sync --frozen --no-dev

# Final stage - smaller image
FROM python:3.14-slim

WORKDIR /app

# Install uv for runtime
RUN pip install --no-cache-dir uv

# Copy the entire project
COPY . .

# Install dependencies (no dev dependencies)
RUN uv sync --frozen --no-dev

# Expose the HTTP MCP port
EXPOSE 9131

# Set environment variables
ENV MCP_PORT=9131
ENV PYTHONUNBUFFERED=1

# Run the MCP server with HTTP transport
CMD ["uv", "run", "--no-dev", "fastmcp", "run", "brainos_server.py:mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "9131"]
