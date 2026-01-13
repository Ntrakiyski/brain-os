# Obsidian MCP Server - HTTP Wrapper
# Builds YuNaga224/obsidian-memory-mcp with Express HTTP wrapper

FROM node:18-alpine

# Install build dependencies
RUN apk add --no-cache git python3 make g++

# Clone and build obsidian-memory-mcp
WORKDIR /app
RUN git clone https://github.com/YuNaga224/obsidian-memory-mcp.git /app/obsidian-memory-mcp

WORKDIR /app/obsidian-memory-mcp
RUN npm install && npm run build

# Install Express for HTTP wrapper
WORKDIR /app
RUN npm install express

# Copy HTTP wrapper
COPY server.mjs /app/server.mjs

# Create vault directory
RUN mkdir -p /vault

ENV MEMORY_DIR=/vault
ENV PORT=8001

EXPOSE 8001

CMD ["node", "/app/server.mjs"]
