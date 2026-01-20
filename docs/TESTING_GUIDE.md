# Brain OS MCP Tools - AI Agent Usage Guide

> **Purpose:** This guide teaches AI agents (Claude, Grok, etc.) how to effectively interact with Brain OS using the **active tools only**. Focus on real-world patterns, best practices, and intelligent tool selection.

> **Active Tools (6 Total - Restart server after changes):**
> 1. `create_memory` - Store new memories (content, sector, salience, entities, observations)
> 2. `get_memory` - Keyword/entity search (use broad query/limit=100 for "get_all_memories")
> 3. `get_memory_relations` - Deep contextual retrieval with relationship exploration
> 4. `query_memories` - AI-powered natural language Q&A with reasoning/confidence
> 5. `summarize_project` - AI synthesis of project memories
> 6. `update_memory_observations` - Refine/add observations to existing memories

---

## 🧠 Core Philosophy (Always Apply)

**Five-Sector Ontology:**
- **Episodic**: Events/meetings ("Client call on Jan 20")
- **Semantic**: Facts/decisions ("FastAPI > Flask for async")
- **Procedural**: How-tos ("Deploy: docker compose up")
- **Emotional**: Feelings ("Frustrated by delays")
- **Reflective**: Insights ("Lock specs early")

**Salience (0.0-1.0):**
- 0.9-1.0: Critical
- 0.7-0.8: Important
- 0.5-0.6: Routine
- Lower for temporary

**Memory Types:**
- `instinctive`: Auto-activates (tech stacks, processes)
- `thinking`: Explicit recall (default)

**Best Practices:**
- ALWAYS specify sector (ask user if unclear)
- Include WHY in observations, WHAT in content
- Use consistent entity names
- High salience for decisions/workflows

---

## 🔧 Tool-by-Tool Guide

### 1. create_memory
**When:** ANY worth remembering info. First tool in most workflows.

**Key Params:**
- `content`: Main fact/event
- `sector`: REQUIRED (one of 5)
- `salience`: 0.0-1.0 (default 0.5)
- `entities`: List ["tech", "client"]
- `observations`: List of insights/rationale
- `memory_type`: "instinctive"/"thinking"

**Example:**
```
create_memory(
  content="Chose FastAPI over Flask: async support, auto-docs, type hints",
  sector="Semantic",
  salience=0.85,
  entities=["FastAPI", "Flask"],
  observations=["2-week eval", "Team 4-1 vote", "Prototype 2x faster"],
  memory_type="instinctive"
)
```

**Tips:**
- Save returned ID for updates/relations
- Batch similar memories together

### 2. get_memory
**When:** Quick keyword/entity lookup. Use `limit=100, query=""` for overview.

**Key Params:**
- `query`: Keywords/entities
- `limit`: Default 20
- `sector`: Filter optional

**Example:**
```
get_memory(query="FastAPI", limit=10)  # Related memories
get_memory(query="", limit=100)         # All memories overview
```

**Tips:**
- Broad query + high limit = "get_all_memories"
- Use for fact-checking before decisions

### 3. get_memory_relations
**When:** Deep dive: "What connects to X?" or complex synthesis.

**Key Params:**
- `query`: Starting point/context
- `depth`: 1-3 (relationships to explore)
- `limit`: Memories per level

**Example:**
```
get_memory_relations(
  query="FastAPI decisions and trade-offs",
  depth=2
)
```

**Tips:**
- Great for decision support
- Returns synthesized insights + sources

### 4. query_memories
**When:** Natural questions: "What did client say?" Use `conversation_history` for context.

**Key Params:**
- `question`: Natural language
- `conversation_history`: List[str] (recent chat)
- `max_memories`: Limit sources

**Example:**
```
query_memories(question="SolarTech concerns?")
conversation_history=["We met Maria CTO", "Dashboard slow"]
```

**Output:** Answer + Reasoning + Confidence + Sources

**Tips:**
- Handles pronouns/coref via history
- Confidence guides reliability

### 5. summarize_project
**When:** Project kickoff/break return: "What's the state?"

**Key Params:**
- `project`: Name (e.g., "Phoenix")
- `limit`: Memories to scan

**Example:**
```
summarize_project(project="BrainOS", limit=50)
```

**Tips:**
- Auto-retrieves + synthesizes
- Identifies gaps/action items

### 6. update_memory_observations
**When:** Refine after new info: Add rationale/insights.

**Key Params:**
- `memory_id`: From create/get
- `new_observations`: List to append

**Example:**
```
update_memory_observations(
  memory_id="123",
  new_observations=["New: Client approved", "Trade-off: +10% cost"]
)
```

**Tips:**
- Non-destructive: Appends only
- Use after meetings/decisions

---

## 🚀 Common Workflows

### Workflow 1: Decision Capture
```
1. get_memory_relations("similar past decisions")
2. query_memories("patterns from history?")
3. User decides → create_memory(..., salience=0.9, instinctive)
4. update_memory_observations(new insights)
```

### Workflow 2: Project Restart
```
1. summarize_project("MyProject")
2. get_instinctive_memory("starting MyProject")  # If uncommented later
3. query_memories("Open issues?")
4. create_memory(new plans)
```

### Workflow 3: Weekly Review
```
1. get_memory(query="", limit=100)
2. summarize_project("all recent")
3. query_memories("Key themes this week?")
4. create_memory(sector="Reflective", summary)
```

### Workflow 4: Client Follow-up
```
1. get_memory("client_name")
2. query_memories("Last discussion points?")
3. create_memory(Episodic, meeting notes)
4. update_memory_observations(observations)
```

---

## 💡 Intelligent Tool Selection

| Need | Tools |
|------|-------|
| Store info | `create_memory` |
| Quick fact | `get_memory` |
| Deep context | `get_memory_relations` |
| Q&A | `query_memories` |
| Project overview | `summarize_project` |
| Refine | `update_memory_observations` |

**Pro Tip:** Start with `query_memories` for user questions—it routes internally.

---

## 🔗 Resources (Read via MCP)
- `brainos://guide`: Full user guide
- `brainos://tool-reference`: Quick ref
- `brainos://philosophy`: Concepts
- `brainos://prompts`: Workflow templates (e.g., "Use weekly_review")

**Example:** "First, read brainos://tool-reference"

## 🎯 AI Agent Best Practices
1. **Explain tool choice:** "Using get_memory_relations because..."
2. **Cite sources:** Always reference memory IDs
3. **Ask for clarification:** Sector unclear? Salience?
4. **Suggest workflows:** "After storing, want a summary?"
5. **Handle empty:** "No memories yet—create some?"
6. **Batch operations:** Create multiple related memories

**You're ready!** Use this to power intelligent Brain OS interactions. 🚀
