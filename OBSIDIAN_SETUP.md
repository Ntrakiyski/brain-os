# Obsidian MCP Integration - Quick Setup

## Status: Ready to Configure

BrainOS is now prepared to work with an external Obsidian MCP service. Just add the URL and it works.

---

## Quick Setup

### 1. Deploy Obsidian MCP (Separate Service)

**Option A: Local Development**
```bash
git clone https://github.com/YuNaga224/obsidian-memory-mcp.git
cd obsidian-memory-mcp
npm install
npm run build
# Run with your vault path
node dist/index.js /path/to/your/vault
```

**Option B: Docker Local**
```bash
docker run -d \
  -p 8001:8001 \
  -v /path/to/vault:/vault \
  yunaga224/obsidian-memory-mcp
```

**Option C: Coolify Production**
- Deploy as separate service in Coolify
- Use internal service URL: `http://obsidian-service:8001/mcp`

---

### 2. Configure BrainOS

**Local Development (.env):**
```env
OBSIDIAN_MCP_URL=http://localhost:8001/mcp
```

**Production (Coolify Environment Variables):**
```
OBSIDIAN_MCP_URL=http://obsidian-service:8001/mcp
```

---

### 3. Restart BrainOS

```bash
# Local
docker compose -f docker-compose.local.yml up -d --build

# Production
# Coolify will auto-redeploy on env var change
```

---

## How It Works

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   BrainOS       │────────▶│  Obsidian MCP   │────────▶│  Obsidian       │
│   (Neo4j)       │  sync   │  (HTTP API)     │  write  │  .md files      │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

**When you create a memory:**
1. Saved to Neo4j (primary)
2. Synced to Obsidian MCP (mirror)
3. `.md` file created in your vault

**When you delete memories:**
- `delete_all_memories()` - Neo4j only (Obsidian files stay)
- `delete_all_memories(cleanup_obsidian=True)` - Both Neo4j and Obsidian

---

## Graceful Degradation

If Obsidian MCP is **not available**:
- ✅ BrainOS continues working normally
- ✅ Neo4j operations unaffected
- ⚠️ Obsidian sync skipped (warning logged)
- ✅ No errors or failures

---

## Testing

Once configured, test the integration:

```python
# Create a memory - should sync to Obsidian
create_memory(
    content="Test memory for Obsidian sync",
    sector="Episodic"
)
```

Check your Obsidian vault for the new `.md` file.

---

## Files Involved

| File | Purpose |
|------|---------|
| `src/utils/obsidian_client.py` | HTTP client for Obsidian MCP |
| `src/database/queries/memory.py` | Calls sync after create |
| `.env.example` | `OBSIDIAN_MCP_URL` configuration |
| `docker-compose.yml` | Environment variable passed to container |

---

## Ready to Use

Just add `OBSIDIAN_MCP_URL` and restart. That's it!
