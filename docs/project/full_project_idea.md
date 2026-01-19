This is the final **MASTER SPECIFICATION for Brain OS**. It is a comprehensive blueprint that combines the philosophy of a living cognitive system with a high-performance, modular technical architecture.

***

# MASTER SPECIFICATION: BRAIN OS
**A Cognitive Operating System for Personal and Professional Intelligence**

## 1. Vision and Philosophy
Brain OS is a cognitive infrastructure designed to transition the human from a manager of details to a director of outcomes. It operates as a **Symbiotic System**: the human (The Brand) provides the soul and strategic direction, while the OS (The Engine) provides the **Metabolic Thinking**—the autonomous processing of data into results. 

The system is designed to learn your specific way of working, offloading technical implementation and routine analysis so you can focus on high-level navigation and final validation.

---

## 2. Memory Architecture: The Synaptic Graph
The system organizes information into a network that mimics human memory, using a graph-native structure to track how ideas and actions evolve.

### 2.1 Bubbles and Clouds
*   **Bubbles (Episodic):** Raw, timestamped moments of experience (transcripts, notes, chat logs). They are the "raw footage" of your life.
*   **Clouds (Synthetic):** AI-generated insights or hypotheses derived from clusters of Bubbles. A Cloud starts as "Pending" and becomes a "Confirmed Understanding" once validated by the human.

### 2.2 The Five-Sector Ontology
Every piece of data is classified into a specific cognitive sector to optimize how the system processes it:
*   **Episodic:** Events and experiences (What happened and when).
*   **Semantic:** Hard facts and knowledge (Requirements, names, technical data).
*   **Procedural:** Habits and workflows (The "My Way" protocol and brand behaviors).
*   **Emotional:** Sentiment and "Vibe" (Tracking morale, frustration, or excitement).
*   **Reflective:** Meta-memory (Logs of how the system is synthesizing information).

### 2.3 The Neurochain (Synaptic Links)
Brain OS uses a "Single-Waypoint" approach to maintain a clean, traversable narrative.
*   **Neural Chains:** Every new Bubble connects only to the single most relevant previous Bubble or Cloud (The "String of Pearls" model).
*   **Synaptic Weight:** Links carry a "strength" value based on usage and a "reason" (e.g., "Dependency," "Contradiction," or "Inspiration").
*   **Neuroplasticity:** If a direction changes, the system "rewires" these chains to reflect the new reality while preserving the historical audit trail.

---

## 3. Cognitive Dynamics: The Thinking Engine
Brain OS manages its own health and retrieval logic through active background processes.

### 3.1 Salience and Adaptive Forgetting
*   **Salience Scoring:** Every memory has a "brightness" score (0.0 to 1.0).
*   **Time-Based Decay:** Low-value information naturally "fades" over time to reduce cognitive load.
*   **Reinforcement:** Accessing or validating a memory boosts its salience, keeping important facts "bright."

### 3.2 Temporal Evolution
*   **Validity Windows:** Uses `valid_from` and `valid_to` timestamps to track how understanding changes.
*   **Audit Trail:** Allows the human to "time travel" and see exactly what the system believed or knew at any past date.

### 3.3 Composite Scoring for Retrieval
The "Creative Partner" retrieves context using a multi-factor formula:
*   **60% Similarity:** Semantic match to the current query.
*   **20% Salience:** The current "brightness" or importance of the memory.
*   **10% Recency:** How fresh the information is.
*   **10% Connection:** How well-linked the memory is to other active nodes.

---

## 4. Fractal DNA: Modular Architecture
The system is built on a hierarchy of reusable components, ensuring logic is created once and inherited everywhere.

*   **Utility Functions (Cells):** Atomic, single-purpose logic (LLM core calls, schema validators, tool bridges).
*   **Specialized Agents (Organs):** Clusters of utility functions designed for specific roles (The Researcher, The Technical Auditor, The Synthesizer).
*   **Workflows (Organisms):** Multi-agent sequences that achieve high-level outcomes (e.g., "The Ingestion Workflow" or "The Weekly Synthesis").

---

## 5. The Symbiotic Membrane: Remote Autonomy
To be fully autonomous, agents have 100% access to the tools they need via live, remote connections to external services.

### 5.1 Remote Server Composition (FastMCP)
Brain OS uses **Live Mounting** to connect to hosted MCP servers.
*   **Remote Proxying:** Brain OS connects to hosted endpoints (e.g., a Gmail or Calendar MCP running on a VPS) via SSE or HTTP.
*   **Dynamic Mounting:** External servers are "mounted" into the Brain OS body. If a remote server is updated with new tools, Brain OS absorbs them instantly without a code restart.

### 5.2 The Heartbeat (Circadian Rhythm)
*   **Background Tasks:** The system runs long-running tasks (Research, Reporting) in the background without blocking the main interface.
*   **Sampling & Elicitation:** The OS can proactively ask the LLM to "think" or ask the human for "validation" when a Cloud needs confirmation.
*   **Maintenance Cycles:** Background cycles for synaptic pruning (decay) and cloud synthesis.

---

## 6. The Division of Labor: Brand vs. Engine
### 6.1 The Brand (The Human Soul)
*   **Navigation:** Setting the destination and high-level intent.
*   **Guidelines:** Defining the "My Way" protocol (preferred tech stacks, voice, and terminology).
*   **Validation:** Acting as the final gatekeeper for "Clouds" and agent outputs.

### 6.2 The Engine (The Metabolic Thinking)
*   **Technical Thinking:** Offloading implementation details (e.g., state management, responsiveness, type safety).
*   **Autonomous CRUD:** Automatically managing tasks and entities based on context.
*   **Memory Maintenance:** Handling decay, salience, and graph health automatically.

---

## 7. Technical Stack
*   **Runtime:** Python 3.14+ (Async-native) managed by **uv**.
*   **MCP Framework:** **FastMCP** (Python SDK) for tools, background tasks, and **Remote Proxy Mounting**.
*   **Agent Framework:** **PocketFlow** (100-line minimalist framework) for workflow orchestration and multi-agent patterns.
*   **Database:** **Neo4j Community Edition** running locally via Docker Compose for development, with production deployment via **Coolify** on **Hetzner VPS**.
*   **Intelligence:** Dual-LLM architecture for optimal cost-performance balance
    *   **Groq** (System 1): Fast actions - classification, extraction, routing. Speed: ~100-200ms.
    *   **OpenRouter** (System 2): Deep thinking - research, synthesis, planning. Quality: Excellent.
*   **Deployment:** **Docker & Docker Compose** for local development, **Coolify** for production hosting.

---

## 8. Value Proposition
*   **Reduced Cognitive Load:** The system naturally forgets what is irrelevant and highlights what matters.
*   **Zero-Prompt Consistency:** Every action follows the "Brand Way" because the Procedural memory is built into the OS.
*   **Accelerated Execution:** Technical implementation and routine research happen in the background, leaving the human to focus solely on high-value decision-making.

***

## 9. The Autonomous Engine (Future Vision)

**Status**: **PLANNED** - Implementation after Obsidian sync phases complete

### 9.1 Phase 3 Scheduled Updates (Pre-Autonomous Engine)

**Note**: Before implementing the full Autonomous Engine described in this section, Phase 3 of the Obsidian integration adds scheduled update capabilities using internal PocketFlow agents.

**Phase 3 Scope** (separate from full Autonomous Engine):
- **Morning Briefing Agent** - Daily summaries of yesterday's memories
- **Evening Recap Agent** - Daily reviews of today's activities
- **Sunday Weekly Review Agent** - Weekly analysis by sector
- **Configuration** - Environment variables (enabled/time/service type)
- **Delivery** - Webhook notifications (Gmail/Telegram)

**Architecture Difference**:
- **Phase 3**: Fixed-time scheduled flows (cron-based, deterministic)
- **Full Engine**: Continuous autonomous cycle (5-10 min intervals, dynamic decision-making)

Phase 3 provides the foundation for autonomous thinking but does not include the full Master Agent, sub-agent specialization, or autonomous decision-making capabilities described below.

### 9.1 The Heartbeat: Autonomous Decision Cycle

Brain OS will run on a continuous autonomous cycle (5-10 minute cron job) that functions as the "metabolic heartbeat" of the system:

```
Every 5-10 minutes:
┌─────────────────────────────────────────────────────────────┐
│  1. MASTER AGENT awakens                                    │
│  2. Queries Neo4j for high-salience memories (>0.7)         │
│  3. Iterates through all pending tasks and decisions        │
│  4. Analyzes patterns, priorities, and context              │
│  5. Routes to appropriate SUB-AGENTS based on task type    │
│  6. Sub-agents execute their specialized functions          │
│  7. Results stored as new memories in the Synaptic Graph   │
│  8. Cycle repeats                                          │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Task Categories and Sub-Agent Specialization

The Master Agent routes work to specialized sub-agents based on task categorization:

| Category | Sub-Agent | Responsibilities |
|----------|-----------|-------------------|
| **Research** | The Researcher | Internet research, documentation review, competitive analysis, fact-checking |
| **Development** | The Builder | Code generation, debugging, testing, deployment, technical implementation |
| **Messaging** | The Communicator | Email responses, notifications, team updates, status reports |
| **Synthesis** | The Synthesizer | Pattern recognition, insight generation, cloud creation, connecting dots |
| **Planning** | The Strategist | Project planning, task breakdown, resource allocation, roadmap generation |
| **Monitoring** | The Guardian | System health checks, error detection, performance monitoring, alerts |

### 9.3 Autonomous Decision-Making Process

```
┌────────────────────────────────────────────────────────────────┐
│                    MASTER AGENT                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  INPUT: High-salience memories + pending tasks          │  │
│  │                                                          │  │
│  │  1. FILTER: Extract memories needing action            │  │
│  │  2. CATEGORIZE: Classify by type (research/dev/msg)     │  │
│  │  3. PRIORITIZE: Sort by salience + deadline + urgency  │  │
│  │  4. ROUTE: Dispatch to appropriate sub-agent           │  │
│  │  5. VALIDATE: Review sub-agent output                  │  │
│  │  6. STORE: Create new memory with results              │  │
│  │                                                          │  │
│  │  OUTPUT: New memories, completed tasks, next actions   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                            │         │
│           ┌────────────┬────────────┬────────────┬──────────┤         │
│           ▼            ▼            ▼            ▼          ▼         │
│       ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│       │Research ││Builder  ││Comm.    ││Plan     │  ...      │
│       │Agent    ││Agent    ││Agent    ││Agent    │            │
│       └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│           │            │            │            │                     │
│           ▼            ▼            ▼            ▼                     │
│       New memories created, actions executed, tasks completed      │
└────────────────────────────────────────────────────────────────┘
```

### 9.4 Sub-Agent Capabilities

**The Researcher (Research Category)**:
- Web search and information gathering
- Documentation analysis and summarization
- Competitive analysis and market research
- Fact-checking and verification
- Source evaluation and citation

**The Builder (Development Category)**:
- Code generation and modification
- Debugging and error resolution
- Test creation and execution
- Deployment automation
- Technical implementation decisions

**The Communicator (Messaging Category)**:
- Email drafting and responses
- Notification management
- Team status updates
- Meeting preparation and summaries
- Follow-up reminders

**The Synthesizer (Synthesis Category)**:
- Pattern recognition across memories
- Cloud generation (Reflective insights)
- Connection discovery between related concepts
- Trend analysis and anomaly detection

**The Strategist (Planning Category)**:
- Project planning and task breakdown
- Resource allocation and scheduling
- Risk assessment and mitigation
- Roadmap generation and milestone tracking

**The Guardian (Monitoring Category)**:
- System health monitoring
- Error detection and alerting
- Performance optimization
- Security and compliance checks

### 9.5 Decision Flow

```
1. AWAKEN: Cron triggers Master Agent (5-10 min interval)
2. RETRIEVE: Query Neo4j for memories WHERE salience > 0.7 AND action_required = true
3. ANALYZE: For each memory, determine:
   - What type of action is needed? (category)
   - How urgent is this? (priority based on salience + deadline)
   - Which sub-agent is best suited?
   - What context does the sub-agent need?
4. DISPATCH: Send task to sub-agent with context
5. EXECUTE: Sub-agent performs specialized function
6. VALIDATE: Master Agent reviews output
7. STORE: Create new memory with results
8. UPDATE: Update original memory with action_taken = true
9. SLEEP: Wait for next cycle
```

### 9.6 Implementation Phases for The Engine

**Phase A: Master Agent Foundation**
- Task scheduling system (cron-based, 5-10 min intervals)
- Memory filtering and prioritization logic
- Task categorization (research/dev/messaging/etc.)
- Sub-agent routing system

**Phase B: Sub-Agent Implementation**
- Implement individual sub-agents
- Specialized tool access for each agent type
- Agent communication protocols
- Result validation and storage

**Phase C: Advanced Decision-Making**
- Multi-step task decomposition
- Cross-agent collaboration
- Learning from past decisions
- Adaptive priority adjustment

**Phase D: Full Autonomy**
- Proactive task generation
- Self-directed goal setting
- Autonomous project management
- Human-in-the-loop validation only for high-impact decisions

### 9.7 Technical Architecture for The Engine

```
0brainOS/
├── src/
│   ├── tasks/
│   │   ├── background.py              # Current: Synaptic pruning, etc.
│   │   ├── autonomous_cycle.py        # NEW: 5-min decision heartbeat
│   │   └── scheduler.py               # NEW: Cron-based task scheduler
│   ├── agents/
│   │   ├── master_agent.py            # NEW: Master decision orchestrator
│   │   ├── sub_agents/
│   │   │   ├── researcher.py          # Research category
│   │   │   ├── builder.py              # Development category
│   │   │   ├── communicator.py        # Messaging category
│   │   │   ├── synthesizer.py          # Synthesis category
│   │   │   ├── strategist.py           # Planning category
│   │   │   └── guardian.py            # Monitoring category
│   │   └── routing/
│   │       ├── categorizer.py         # Task categorization logic
│   │       ├── prioritizer.py          # Priority scoring
│   │       └── dispatcher.py           # Sub-agent routing
│   └── flows/
│       └── autonomous_decision.py     # PocketFlow for decision cycle
```

### 9.8 Design Principles for The Engine

1. **Human Authority**: Master Agent proposes, Human decides for high-impact actions
2. **Transparent Logging**: Every autonomous action is logged and queryable
3. **Graceful Degradation**: If a sub-agent fails, log error and continue
4. **Incremental Autonomy**: Start with read-only actions, gradually enable write actions
5. **Context Preservation**: All decisions reference source memories
6. **Audit Trail**: Every autonomous action creates a new memory

---

**End of Specification.**