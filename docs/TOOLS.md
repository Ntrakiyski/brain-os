# Brain OS Tools Documentation

Complete reference for all Brain OS MCP tools with inputs, outputs, examples, and usage guidance.

---

## Table of Contents

1. [Memory Management](#memory-management)
2. [Memory Retrieval](#memory-retrieval)
3. [Memory Visualization](#memory-visualization)
4. [System Monitoring](#system-monitoring)
5. [Email Notifications](#email-notifications)
6. [Agents](#agents)

---

## Memory Management

### create_memory

Store a new memory in the Synaptic Graph.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| content | string | Yes | - | What to remember (include WHY, not just WHAT) |
| sector | string | Yes | - | Cognitive sector: Episodic, Semantic, Procedural, Emotional, Reflective |
| salience | float | No | 0.5 | Importance: 0.9-1.0 (critical), 0.7-0.8 (important), 0.5-0.6 (routine) |
| source | string | No | "direct_chat" | Origin of the data |
| entities | list[str] | No | [] | Named entities (people, projects, technologies) |
| observations | list[str] | No | [] | Supporting details and context |
| memory_type | string | No | "thinking" | Type: "thinking" (default), "instinctive" (auto-activate) |
| activation_threshold | float | No | 0.65 | When instinctive (0.0-1.0, lower = more sensitive) |

**Output:**
```
Memory stored successfully!

ID: 4
Sector: Episodic
Salience: 0.80
Created: 2026-01-14 13:50:41 UTC
```

**Example:**
```python
create_memory(
    content="Chose PostgreSQL over MongoDB for ACID compliance and transaction support",
    sector="Semantic",
    salience=0.85,
    entities=["PostgreSQL", "MongoDB"],
    observations=["Evaluated both databases", "ACID compliance required", "Transaction support needed"]
)
```

**Best Practices:**
- Include decision rationale in observations
- Use consistent entity names
- Set salience based on long-term value
- Use `memory_type="instinctive"` for frequently-accessed context

---

### delete_memory

Delete a specific memory by ID (soft deletion with audit trail).

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| bubble_id | string | Yes | - | Simple numeric ID (e.g., "4") |
| confirm | bool | Yes | False | Set to True to confirm deletion |

**Output:**
```
## Memory Deleted Successfully

**ID**: 4
**Sector**: Semantic
**Content**: Chose PostgreSQL over MongoDB...

The memory has been soft-deleted (valid_to timestamp set).
Audit trail is preserved in the database.
```

**Example:**
```python
delete_memory(bubble_id="4", confirm=True)
```

**Note:** Soft deletion preserves audit trail. Use `get_all_memories()` to find bubble IDs.

---

### delete_all_memories

Delete ALL memories from the Synaptic Graph.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| cleanup_obsidian | bool | No | False | If True, also delete Obsidian .md files |

**Output:**
```
## All Memories Deleted Successfully

**Deleted**: 5 memories

**Obsidian**: .md files NOT deleted (set cleanup_obsidian=True to delete)

The Synaptic Graph has been cleared.
All memories have been soft-deleted (valid_to timestamp set).
```

**Example:**
```python
# Delete from Neo4j only
delete_all_memories()

# Delete from Neo4j AND Obsidian
delete_all_memories(cleanup_obsidian=True)
```

---

## Memory Retrieval

### get_memory

Quick keyword search for specific memories.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Search term (keyword, entity name, etc.) |
| limit | int | No | 10 | Maximum results to return |
| memory_type | string | No | None | Filter: "thinking", "instinctive", or None (all) |

**Output:**
```
Found 2 memories matching 'Alice':

1. ID: 0 | Sector: Episodic | Salience: 0.80
   Alice fell down the rabbit hole and entered Wonderland...

2. ID: 1 | Sector: Episodic | Salience: 0.70
   Alice encountered the Cheshire Cat in the forest...
```

**Example:**
```python
get_memory(query="Alice", limit=5)
get_memory(query="PostgreSQL", memory_type="thinking")
```

**Use For:** Quick lookup when you know what you're searching for.

---

### get_all_memories

Get complete overview with statistics.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | int | No | 100 | Maximum results to return |

**Output:**
```
## Brain OS Memory Overview

**Total Memories**: 12
**Average Salience**: 0.68

### Sector Distribution:
- Semantic: 5 (41.7%)
- Episodic: 4 (33.3%)
- Procedural: 2 (16.7%)
- Reflective: 1 (8.3%)
- Emotional: 0 (0.0%)

### Recent Memories:
1. ID: 11 | Episodic | Salience: 0.70
   Alice discovered she could use her growing...

[... more memories ...]
```

**Example:**
```python
get_all_memories(limit=50)
```

**Use For:** Starting work, checking cognitive state, getting statistics.

---

### get_instinctive_memory

Auto-activate memories based on context (the "Oven Analogy").

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| user_input | string | Yes | - | Context: what you're working on right now |
| limit | int | No | 10 | Maximum memories to return |

**Output:**
```
## Instinctive Memories Activated

Found 2 instinctive memories for: "Starting work on FastTrack project"

1. FastTrack_Billing_Rate (Episodic, Salience: 0.85)
   Client approved €60/hour for 20 hours...

2. FastTrack_N8n_Workflow (Procedural, Salience: 0.75)
   N8N workflow automation setup process...
```

**Example:**
```python
get_instinctive_memory(user_input="Starting work on FastTrack project", limit=5)
```

**Use For:** Context switching, starting work on a project, automatic memory activation.

**Note:** Requires memories with `memory_type="instinctive"` to be created first.

---

### get_memory_relations

Deep contextual retrieval with synthesis.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Your question or topic |
| limit | int | No | 10 | Maximum memories to retrieve |
| depth | int | No | 2 | How many relationship hops to explore (1-3) |

**Output:**
```
## Related Memories: PostgreSQL Decision

### Overview
3 relevant memories found exploring database technology choices.

### Key Insights
1. PostgreSQL chosen for ACID compliance (Semantic, Salience: 0.85)
2. Transaction support was critical requirement (Procedural, Salience: 0.75)
3. Evaluated MongoDB but rejected due to lack of transactions (Semantic, Salience: 0.70)

### Themes
- ACID compliance
- Transaction support
- Database consistency

### Recommendations
Consider PostgreSQL for future projects requiring strong consistency.
```

**Example:**
```python
get_memory_relations(query="Why did we choose PostgreSQL?", limit=10, depth=2)
```

**Use For:** Deep understanding, exploring themes, finding connections, decision rationale.

---

### query_memories_tool (NEW - Phase 6)

AI-powered Q&A with reasoning and confidence scores.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Your natural language question |
| conversation_history | list[str] | No | [] | Recent messages for context (helps with pronouns) |

**Output:**
```
## Answer
You met with Alice on January 10, 2026, to discuss N8N workflow integration for the FastTrack project.

## Reasoning
Found memory [1] which records the meeting on 2026-01-10 about N8N workflow
with Alice from FastTrack. The meeting was documented as an Episodic memory
with high salience (0.85), indicating it was important.

## Confidence
0.92 / 1.0 (Very Confident)

## Sources
1 memory entries used
```

**Example:**
```python
query_memories_tool(query="When did I meet with Alice?")

query_memories_tool(
    query="What did we decide about the project timeline?",
    conversation_history=["We discussed the sprint", "Alice suggested 2 weeks"]
)
```

**Use For:**
- Direct questions requiring answers ("When did I...?", "Why did we...?")
- Decision rationale ("Why did I choose X?")
- Summaries ("Summarize my work with...")
- Opinion/attitude queries ("What does Alice think about...?")
- Temporal queries ("What happened last week?")

---

## Memory Visualization

### list_sectors

Show cognitive sector distribution and statistics.

**Inputs:** None

**Output:**
```
## Brain OS Sector Distribution

### Current Distribution:
Episodic.............. 4 (33%)
Semantic.............. 5 (42%)
Procedural............. 2 (17%)
Emotional.............. 0 (0%)
Reflective............. 1 (8%)

Total Memories: 12

### Cognitive Balance:
✓ Healthy distribution across sectors
Consider adding Emotional memories for work-life balance
```

**Example:**
```python
list_sectors()
```

**Use For:** Checking cognitive balance, identifying gaps in memory types.

---

### visualize_memories

ASCII visualization with charts.

**Inputs:** None

**Output:**
```
## Brain OS Memory Visualization

Total Memories: 12

### Sector Distribution:
Episodic (4)  ████████████░░ 33%
Semantic (5)   ██████████████ 42%
Procedural (2)  ████░░░░░░░░░░░░ 17%
Reflective (1)  ██░░░░░░░░░░░░░░  8%

### Salience Distribution:
0.9-1.0 (3)   ████████░░░░░ 25%
0.7-0.8 (4)   ██████████░░░░ 33%
0.5-0.6 (3)   ████████░░░░░ 25%
0.3-0.4 (1)   ████░░░░░░░░░░  8%
0.0-0.2 (1)   ████░░░░░░░░░░  8%
```

**Example:**
```python
visualize_memories()
```

**Use For:** Visual overview, pattern recognition, presentations.

---

### visualize_relations

Visualize explicit relationships between memories.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| bubble_id | string | Yes | - | Simple numeric ID (e.g., "4") |
| depth | int | No | 2 | Hops to explore (1-4) |
| format | string | No | "mermaid" | "mermaid" for inline, "neo4j" for browser query |

**Output:**
```
## Memory Relationships

**Bubble ID**: 0
**Content**: Alice fell down the rabbit hole...
**Found**: 2 relationships

### Mermaid Diagram
```mermaid
graph LR
    B1["0: Alice fell down..."]
    B2["1: Alice encountered..."]
    B1 -->|relates_to| B2
```
```

**Alternative (No Relationships):**
```
## Memory Relationships: No Connections Found

This memory has no explicit connections to other memories yet.

**To Explore Related Content:**
- get_memory_relations(query="related topic")
- get_memory(query="keyword")
- get_all_memories()
```

**Example:**
```python
visualize_relations(bubble_id="0", depth=2)
visualize_relations(bubble_id="4", format="neo4j")
```

**Use For:** Understanding knowledge clusters, exploring explicit connections.

**Note:** This tool shows **explicit** LINKED relationships. For **semantic/contextual** relationships, use `get_memory_relations`.

---

## System Monitoring

### get_system_health

Comprehensive system status check.

**Inputs:** None

**Output:**
```
## Brain OS System Health

### Neo4j Database
✅ Connected: bolt://localhost:7687
Version: Neo4j/5.25-community

### Memory Statistics
Total memories: 12
Active memories: 12
Deleted memories: 0
Average salience: 0.68

### LLM Providers
Groq: ✅ Healthy (openai/gpt-oss-120b)
OpenRouter: ✅ Healthy (anthropic/claude-sonnet-4)

### Background Tasks
Circadian Pruning: Scheduled (every 24h)
Cloud Synthesis: Scheduled (every 168h)
Health Check: Scheduled (every 1h)

### Overall Status
✅ All systems operational
```

**Example:**
```python
get_system_health()
```

**Use For:** Troubleshooting, health checks, deployment verification.

---

### get_task_status

Query background task status and schedule.

**Inputs:** None

**Output:**
```
## Background Task Status

### Scheduled Tasks
| Task | Frequency | Last Run | Next Run | Status |
|------|-----------|----------|----------|--------|
| Circadian Pruning | 24h | 2026-01-14 08:00 | 2026-01-15 08:00 | Scheduled |
| Cloud Synthesis | 168h | 2026-01-13 06:00 | 2026-01-20 06:00 | Scheduled |
| Health Check | 1h | 2026-01-14 15:00 | 2026-01-14 16:00 | Scheduled |

### Task History
[No recent task executions]
```

**Example:**
```python
get_task_status()
```

**Use For:** Monitoring automated maintenance, checking task schedules.

---

## Email Notifications

### send_email

Send a direct email notification via webhook.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| subject | string | Yes | - | Email subject line |
| body | string | Yes | - | Email body content |
| webhook_url | string | No | env var | Your webhook URL |
| metadata | string | No | "" | JSON metadata for tracking |
| authorization | string | No | env var | Auth token (if required) |

**Output:**
```
✅ Email notification sent successfully!

Subject: Brain OS Alert
Status: 200
Sent: 2026-01-14T15:30:00Z

Your email should arrive shortly.
```

**Example:**
```python
send_email(
    subject="Brain OS Alert",
    body="Your weekly summary is ready!"
)
```

**Use For:** Custom notifications, alerts, test emails.

---

### send_templated_email_tool

Send email using pre-built templates.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| template | string | Yes | - | Template: weekly_summary, cloud_insight, system_alert, task_report |
| variables | string | Yes | - | JSON string of template variables |
| webhook_url | string | No | env var | Your webhook URL |
| authorization | string | No | env var | Auth token |

**Output:**
```
✅ Templated email sent successfully!

Template: weekly_summary
Subject: Brain OS Weekly Cognitive Summary
Sent: 2026-01-14T15:30:00Z

Your email should arrive shortly.
```

**Available Templates:**

**weekly_summary:**
```json
{
  "total_memories": 147,
  "new_memories": 12,
  "sector_distribution": "Semantic: 35%, Procedural: 30%...",
  "insights": "1. FastTrack project shows scope creep...",
  "pruning_status": "✓ Complete",
  "synthesis_status": "✓ Complete",
  "health_status": "✓ Healthy"
}
```

**cloud_insight:**
```json
{
  "insight_content": "Project shows scope creep pattern",
  "related_count": 5,
  "salience": 0.8
}
```

**system_alert:**
```json
{
  "alert_type": "Database Connection Failed",
  "alert_message": "Cannot connect to Neo4j",
  "severity": "critical",
  "component": "database",
  "action": "Check Neo4j service"
}
```

**task_report:**
```json
{
  "task_name": "Circadian Pruning",
  "status": "success",
  "start_time": "2026-01-14 08:00:00",
  "end_time": "2026-01-14 08:05:00",
  "duration": "5 minutes",
  "results": "Pruned 3 memories with low salience"
}
```

**Example:**
```python
send_templated_email_tool(
    template="cloud_insight",
    variables='{"insight_content": "New insight generated", "related_count": 5, "salience": 0.8}'
)
```

**Use For:** Automated notifications, background task reports, system alerts.

---

### list_email_templates

List all available email templates with required variables.

**Inputs:** None

**Output:**
```
## Brain OS Email Templates

Available templates for `send_templated_email_tool`:

### weekly_summary
**Subject:** Brain OS Weekly Cognitive Summary
**Variables:**
  - total_memories
  - new_memories
  - sector_distribution
  - insights
  - pruning_status
  - synthesis_status
  - health_status

### cloud_insight
**Subject:** Brain OS: New Reflective Insight Generated
**Variables:**
  - insight_content
  - related_count
  - salience

[... more templates ...]
```

**Example:**
```python
list_email_templates()
```

**Use For:** Discovering available templates and their variables.

---

### test_email_webhook

Test your email webhook configuration.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| webhook_url | string | No | env var | Your webhook URL to test |
| authorization | string | No | env var | Auth token |

**Output:**
```
✅ Test email sent successfully!

Your webhook is working! Check your email inbox.

If you don't see the email within a minute:
- Check your spam folder
- Verify the webhook URL is correct
- Check your webhook service (Make.com, etc.) is active

Webhook URL: https://n8n.trakiyski.work/webhook/abc123
Status: 200
Timestamp: 2026-01-14T14:39:25Z
```

**Example:**
```python
test_email_webhook()
```

**Use For:** Verifying webhook setup, troubleshooting email delivery.

---

## Agents

### summarize_project

AI-powered project summaries using PocketFlow.

**Inputs:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| project | string | Yes | - | Project name to summarize |
| limit | int | No | 10 | Maximum memories to include |

**Output:**
```
# Project Summary: Wonderland

**Source:** 3 memories analyzed
**Flow:** summarize_project_flow (PocketFlow)

---

# Project Summary: Wonderland

## Overview
Wonderland is a narrative project depicting Alice's adventures in a fantastical realm with inverted logic, dramatic size changes, and impossible events. Key elements include Alice's entry via the rabbit hole and her use of growing/shrinking abilities to navigate obstacles.

## Key Decisions
- No explicit decisions documented in memories.

## Action Items
- No outstanding tasks identified.

## Notes
- **Procedural Memory** (2026-01-14, Salience: 0.70): Alice uses growing/shrinking to navigate and escape dangers.
- **Semantic Memory** (2026-01-14, Salience: 0.80): Wonderland features inverted logic, size fluctuations, and regular impossibilities.
- **Episodic Memory** (2026-01-14, Salience: 0.80): Alice enters Wonderland by falling down the rabbit hole from the riverbank.
```

**Example:**
```python
summarize_project(project="Wonderland", limit=5)
summarize_project(project="FastTrack", limit=10)
```

**Use For:** Project overviews, catching up after a break, understanding project context.

---

## Tool Selection Guide

| Need | Use |
|------|-----|
| **Store information** | create_memory |
| **Quick keyword lookup** | get_memory |
| **Direct Q&A** | query_memories_tool |
| **Start work / Context switch** | get_instinctive_memory |
| **Deep understanding** | get_memory_relations |
| **Project overview** | summarize_project |
| **Check balance** | list_sectors |
| **See patterns** | visualize_memories |
| **Explore connections** | visualize_relations |
| **Delete memory** | delete_memory |
| **Delete all** | delete_all_memories |
| **System health** | get_system_health |
| **Send notification** | send_email |
| **Email templates** | list_email_templates |

---

## Common Workflows

### Starting Work on a Project
```python
# 1. Get instinctive memories
get_instinctive_memory("Starting work on FastTrack")

# 2. Get project summary
summarize_project("FastTrack")

# 3. Ask questions
query_memories_tool("What's the current status of FastTrack?")
```

### Understanding a Decision
```python
# 1. Quick lookup
get_memory("PostgreSQL")

# 2. Deep context
get_memory_relations("Why PostgreSQL?")

# 3. Direct answer
query_memories_tool("Why did I choose PostgreSQL over MongoDB?")
```

### Weekly Review
```python
# 1. Get overview
get_all_memories(limit=50)

# 2. Check balance
list_sectors()

# 3. Visualize patterns
visualize_memories()

# 4. Generate summary
query_memories_tool("Summarize my week and what I learned")
```

### Cognitive Housekeeping
```python
# 1. Check system health
get_system_health()

# 2. Review task schedule
get_task_status()

# 3. Send weekly summary
send_templated_email_tool(
    template="weekly_summary",
    variables='{"total_memories": 147, "new_memories": 12, ...}'
)
```

---

## Tips & Best Practices

### Memory Creation
- **Include WHY, not just WHAT**: "Chose PostgreSQL for ACID compliance" vs "Chose PostgreSQL"
- **Use consistent entity names**: "FastTrack" not "fasttrack" or "Fast Track"
- **Set appropriate salience**: 0.9-1.0 for critical decisions, 0.5-0.6 for routine
- **Add observations**: Capture decision rationale, constraints, outcomes

### Memory Retrieval
- **Start with `query_memories_tool`** for direct questions
- **Use `get_memory_relations`** for deep exploration
- **Use `get_instinctive_memory`** when starting work
- **Use `get_all_memories`** to see everything

### Confidence Scores
- **0.9-1.0 (Very Confident)**: Direct match, high salience, multiple sources
- **0.75-0.9 (Confident)**: Good match, some uncertainty
- **0.5-0.75 (Moderately Confident)**: Partial match, hedge words
- **0.3-0.5 (Low Confidence)**: Weak match, limited info
- **0.0-0.3 (Uncertain)**: No relevant data found

---

## Environment Setup

### Required Environment Variables
```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Groq (fast classification)
GROQ_API_KEY=your-groq-key
GROG_QUICK_MODEL=openai/gpt-oss-120b

# OpenRouter (deep synthesis)
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_RESEARCHING_MODEL=anthropic/claude-sonnet-4
OPENROUTER_CREATIVE_MODEL=anthropic/claude-sonnet-4
OPENROUTER_PLANNING_MODEL=anthropic/claude-opus-4

# Email (optional)
EMAIL_WEBHOOK_URL=https://n8n.trakiyski.work/webhook/abc123
EMAIL_AUTHORIZATION=your-auth-token

# Obsidian (optional)
OBSIDIAN_MCP_URL=http://obsidian-mcp:8001/mcp
```

---

**Documentation Version**: Phase 6 Complete
**Last Updated**: 2026-01-14
**Total Tools**: 18
