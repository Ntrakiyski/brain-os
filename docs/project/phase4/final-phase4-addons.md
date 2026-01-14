# Phase 4 Additions: Email Notifications + Phoenix Cloud Observability

> **Status**: Implementation Complete | **Date**: 2026-01-09
> **Your Configuration**: N8N webhook + Phoenix Cloud observability

---

## Quick Summary

Two powerful extensions to Phase 4:

1. **Email/Webhook Notifications** - Pre-configured with your N8N webhook
2. **Phoenix Cloud Observability** - Managed LLM tracing dashboard (no containers needed!)

---

## Part 1: Email Notifications (N8N + Your Webhook)

### Your Pre-Configured Setup

**Webhook URL:** `https://n8n.trakiyski.work/webhook/7887310e-c19d-4280-8018-9db363263d39`
**Authorization:** `sf1Y4TZ3iRporOfxKfGwSeejlbkyoIoB`

Both are **pre-configured** as defaults in the tools!

### New Tools (4)

#### TOOL 13: send_email

Send a custom email notification.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | string | No | Your N8N URL | Pre-configured |
| `subject` | string | Yes | - | Email subject |
| `body` | string | Yes | - | Email body |
| `metadata` | string | No | "" | JSON metadata |
| `authorization` | string | No | Your auth token | Pre-configured |

**Usage:**
```
send_email(
    subject="Brain OS Alert",
    body="Your weekly summary is ready!"
)
```

---

#### TOOL 14: send_templated_email

Send a pre-built template email.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `webhook_url` | string | No | Your N8N URL | Pre-configured |
| `template` | string | Yes | - | Template name |
| `variables` | string | Yes | - | JSON variables |
| `authorization` | string | No | Your auth token | Pre-configured |

**Available Templates:**

| Template | Purpose | Variables |
|----------|---------|-----------|
| `weekly_summary` | Weekly cognitive report | total_memories, new_memories, sector_distribution, insights, pruning_status, synthesis_status, health_status |
| `cloud_insight` | New Reflective memory | insight_content, related_count, salience |
| `system_alert` | System warning | alert_type, alert_message, severity, component, action |
| `task_report` | Task completion | task_name, status, start_time, end_time, duration, results |

---

#### TOOL 15: test_email_webhook

Test your N8N webhook configuration.

**Just run it!** Your webhook URL and auth are pre-configured:
```
test_email_webhook()
```

---

#### TOOL 16: list_email_templates

List all available email templates with required variables.

---

### N8N Workflow Setup

In your N8N instance, create this workflow:

```
Webhook → Gmail/SendGrid
  ↓
{
    "subject": "...",
    "body": "...",
    "is_html": false,
    "timestamp": "...",
    "metadata": {...}
  }
  ↓
Send Email
```

**N8N Node Configuration:**

1. **Webhook Node**: Set to POST (your webhook is already configured)
2. **Send Email Node**: Map the JSON fields
   - `subject` → Email Subject
   - `body` → Email Body
   - `metadata` → Custom headers (optional)

---

## Part 2: Phoenix Cloud Observability

### Why Phoenix Cloud?

**Phoenix Cloud is perfect for Brain OS:**

| Feature | Benefit for Brain OS |
|---------|----------------------|
| **Managed Service** | No containers to manage, instant setup |
| **OpenTelemetry Native** | Standard tracing protocol |
| **LLM Focused** | Built for tracing LLM applications |
| **Interactive Playground** | Test prompts and debug |
| **Evaluation Library** | Pre-built eval templates |
| **Dataset Clustering** | Find semantic patterns in memories |
| **Free Tier** | Generous free tier for development |

### Architecture

```
Brain OS (MCP Server)
    ↓
OpenTelemetry Traces
    ↓
Phoenix Cloud (app.phoenix.arize.com)
    ↓
Phoenix Dashboard (cloud UI)
```

---

### Setup Phoenix Cloud for Brain OS

#### Step 1: Get Phoenix Cloud Credentials

1. Sign up at https://phoenix.arize.com/
2. Create a new project
3. Get your credentials:
   - **Collector Endpoint**: e.g., `https://app.phoenix.arize.com/v1/traces`
   - **API Key**: Your authentication token
   - **Project URL**: e.g., `https://app.phoenix.arize.com/projects/your-project-id`

---

#### Step 2: Install Phoenix Dependencies

```bash
# Add to pyproject.toml
uv add arize-phoenix-otel
```

Update `pyproject.toml`:

```toml
dependencies = [
    # ... existing ...
    "httpx>=0.27.0",
    "arize-phoenix-otel>=0.1.0",
]
```

---

#### Step 3: Configure Environment Variables

Add to `.env` (or set in Coolify):

```env
# Phoenix Cloud Observability
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-username
PHOENIX_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important**: The `arize-phoenix-otel` package automatically picks up these environment variables. No hardcoded credentials in the code!

**Note**: Your endpoint format will be `https://app.phoenix.arize.com/s/your-username` (not `/v1/traces`).

---

#### Step 4: Phoenix Integration is Already Complete!

The `src/utils/observability.py` file already includes:

✅ **arize-phoenix-otel integration** - Uses simplified Phoenix OTEL package
✅ **Automatic environment variable pickup** - Reads PHOENIX_API_KEY and PHOENIX_COLLECTOR_ENDPOINT
✅ **Convenience classes** - `BrainOSTracer` for easy tracing
✅ **Decorator** - `@instrument_mcp_tool` for automatic tool tracing
✅ **Auto-setup** - Tracing initializes on import

No additional code changes needed!

---

#### Step 5: Trace MCP Tool Calls (Optional)

Add tracing to specific tools (example):

```python
# src/tools/memory/create_memory.py

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@mcp.tool
async def create_memory(
    content: str,
    sector: str,
    ...
) -> str:
    """Store a new memory."""
    with tracer.start_as_current_span("create_memory") as span:
        # Add attributes
        span.set_attribute("brainos.tool", "create_memory")
        span.set_attribute("brainos.sector", sector)
        span.set_attribute("brainos.content_length", len(content))

        try:
            # ... create memory logic ...
            span.set_attribute("brainos.success", True)
            span.set_attribute("brainos.memory_id", result.id)
        except Exception as e:
            span.set_attribute("brainos.success", False)
            span.set_attribute("brainos.error", str(e))
            span.record_exception(e)
            raise
```

---

#### Step 6: Add Phoenix Health Check to Server (Optional)

Update `brainos_server.py`:

```python
# Add to imports
from src.utils.observability import setup_phoenix_tracing, PHOENIX_UI_URL

# After creating mcp instance
setup_phoenix_tracing()

# Add Phoenix health check
@mcp.custom_route("/phoenix-status", methods=["GET"])
async def phoenix_status(request) -> JSONResponse:
    """Check Phoenix tracing status."""
    return JSONResponse({
        "status": "tracing_enabled",
        "phoenix_ui": PHOENIX_UI_URL,
        "otel_endpoint": os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "not configured")
    })
```

---

### Environment Variables

Add to `.env` (or set in Coolify):

```env
# Email Notifications (N8N) - Set your actual values here
EMAIL_WEBHOOK_URL=your-n8n-webhook-url-here
EMAIL_AUTHORIZATION=your-n8n-auth-token-here

# Phoenix Cloud Observability - Get from Phoenix Cloud Settings
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-username
PHOENIX_API_KEY=your-phoenix-api-key-here
```

**Important Security Notes:**
- Never commit `.env` files to git (already in `.gitignore`)
- Do NOT hardcode credentials in Python code
- All tools read these values from environment variables automatically
- In Coolify, set these in the environment variables section, not in files

---

### What Phoenix Will Track

**For each MCP tool call:**

| Attribute | Description | Example |
|-----------|-------------|---------|
| `brainos.tool` | Tool name | `create_memory` |
| `brainos.sector` | Cognitive sector | `Semantic` |
| `brainos.salience` | Salience score | `0.8` |
| `brainos.success` | Success status | `true` |
| `brainos.latency_ms` | Execution time | `145` |
| `brainos.memory_id` | Created ID | `4:abc123...` |
| `brainos.error` | Error message | `Connection timeout` |

---

### Phoenix Dashboard Features

**Traces View:**
- See every MCP tool call
- Timeline of execution
- Parent-child relationships (flows)
- Error tracking

**Evaluations:**
- Pre-built templates for quality
- Custom evals for Brain OS
- Human feedback integration

**Datasets:**
- Clustering of similar queries
- Semantic search in traces
- Performance patterns

---

### Quick Start Commands

```bash
# Install dependencies
uv sync

# Set environment variables (replace with your actual values)
export PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-username
export PHOENIX_API_KEY=your-actual-api-key-here

# Run Brain OS with Phoenix Cloud tracing
python brainos_server.py

# Open Phoenix Cloud Dashboard
# https://app.phoenix.arize.com
```

---

## Background Tasks with Email + Phoenix

### Example: Weekly Summary with Notifications

```python
# src/tasks/background.py

@mcp.background_task(interval_hours=168)  # Weekly
async def weekly_summary_task():
    """Generate weekly summary and email it."""
    from opentelemetry import trace
    from src.utils.notifications import send_weekly_summary_email

    tracer = trace.get_tracer("background_tasks")

    with tracer.start_as_current_span("weekly_summary") as span:
        span.set_attribute("task.type", "weekly_summary")

        # Gather statistics
        stats = await gather_statistics()
        span.set_attribute("stats.total_memories", stats["total_memories"])

        # Send email
        result = await send_weekly_summary_email(
            webhook_url=os.getenv("EMAIL_WEBHOOK_URL"),
            stats=stats,
            headers={"Authorization": os.getenv("EMAIL_AUTHORIZATION")}
        )

        span.set_attribute("email.success", result["success"])

        logger.info("Weekly summary complete")
```

---

## Updated Dependencies

`pyproject.toml`:

```toml
dependencies = [
    "fastmcp>=2.14.2",
    "neo4j>=5.25.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.10.0",
    "groq>=0.11.0",
    "openai>=1.57.0",
    "pocketflow>=0.0.3",
    "httpx>=0.27.0",           # NEW: Webhook HTTP client
    "arize-phoenix-otel>=0.1.0",  # NEW: Phoenix Cloud OTEL integration
]
```

---

## Files Created/Modified

### New Files:
- `src/utils/notifications.py` - Email notification utility (reads from env vars)
- `src/utils/observability.py` - Phoenix Cloud tracing setup (arize-phoenix-otel)
- `src/tools/notifications/__init__.py` - MCP tool wrappers (no hardcoded credentials)

### Modified Files:
- `src/tools/__init__.py` - Export notification registration
- `brainos_server.py` - Register notification tools
- `pyproject.toml` - Added httpx, arize-phoenix-otel
- `docker-compose.yml` - No Phoenix containers needed (Cloud version), PHOENIX_* env vars
- `.env.example` - Added EMAIL_WEBHOOK_URL, EMAIL_AUTHORIZATION, PHOENIX_COLLECTOR_ENDPOINT, PHOENIX_API_KEY

---

## Testing Your Setup

### Test Email Notifications:

```
# In Claude Desktop or MCP client:
test_email_webhook()
```

**Expected result:** Test email in your inbox!

---

### Test Phoenix Observability:

```bash
# Set environment variables (replace with your actual values)
export PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com/s/your-username
export PHOENIX_API_KEY=your-actual-api-key-here

# Run Brain OS
python brainos_server.py

# Use some tools:
# - create_memory
# - get_memory
# - get_memory_relations

# Open Phoenix Cloud Dashboard:
# https://app.phoenix.arize.com
```

**Expected result:** See traces for each tool call in Phoenix Cloud!

---

## Quick Reference Card

| Feature | Command/URL |
|---------|-------------|
| **Send email** | `send_email(subject="Test", body="Hello")` |
| **Send template** | `send_templated_email(template="weekly_summary", variables='{"total": 100}')` |
| **Test webhook** | `test_email_webhook()` |
| **Phoenix Cloud UI** | https://app.phoenix.arize.com |
| **Health check** | http://localhost:9131/phoenix-status |

---

## Troubleshooting

### Email Not Sending:

1. Check N8N webhook is active
2. Verify authorization token is correct
3. Check N8N execution logs
4. Test with `test_email_webhook()`

### Phoenix Not Showing Traces:

1. Verify environment variables are set: `echo $PHOENIX_COLLECTOR_ENDPOINT`
2. Check API key is valid: https://app.phoenix.arize.com
3. Verify endpoint starts with `https://` for Phoenix Cloud
4. Check Phoenix Cloud UI for incoming traces
5. Verify instrumentation in `brainos_server.py`

---

## Success Criteria

| Feature | Target | Status |
|---------|--------|--------|
| **Email Notifications** | 4 tools with your webhook | ✅ Complete |
| **Phoenix Cloud** | Tracing dashboard active | ✅ Ready |
| **Background Tasks** | Tasks send emails | ✅ Ready |
| **Dependencies** | All added to pyproject.toml | ✅ Complete |
| **No Containers Needed** | Phoenix Cloud (managed service) | ✅ Complete |

---

**End of Phase 4 Additions**
