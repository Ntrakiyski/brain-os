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

**End of Specification.**