# Dynamic salience scoring for cognitive memory agents
https://claude.ai/chat/3a13a230-1784-4870-95e4-7a0432ac57e2

Processing 20-minute voice notes into a persistent, high-quality memory graph requires a salience scoring system that compounds in value over time. The optimal architecture combines **retrieval-augmented scoring** (using Neo4j to compare against existing memories) with a **hybrid static-adaptive approach** that resists calibration drift. Production systems like Stanford's Generative Agents, MemGPT, and Mem0 demonstrate that multi-factor scoring—combining recency, emotional intensity, novelty, and actionability—outperforms single-dimension importance ratings. For your PocketFlow + FastMCP + Neo4j stack, the recommended pattern is a three-phase pipeline: retrieve similar memories → compute structured salience scores → persist with graph relationships, using Groq's structured outputs for fast, reliable 0-1 scoring.

---

## The retrieval-augmented scoring pattern delivers compounding quality

The most effective architectural approach for your use case combines tool-based scoring with retrieval augmentation rather than relying on pure LLM judgment. Before scoring each new memory, query Neo4j for similar existing memories using vector similarity, then compute salience based on actual novelty against the memory graph.

**Three architectural patterns compared:**

| Approach | Latency | Quality | Compounding Benefit |
|----------|---------|---------|---------------------|
| Dedicated sub-agent | High (~300ms/memory) | Excellent | Manual—requires retraining |
| Tool-based (`suggest_salience`) | Medium | Good | Limited—single context |
| **Retrieval-augmented hybrid** | Low | Excellent | **Automatic—adapts as corpus grows** |

The retrieval-augmented approach excels because novelty computed against actual existing memories is more reliable than LLM estimation. Zep AI's Graphiti implementation achieves **P95 latency of 300ms** for this pattern. The cold-start problem (limited effectiveness with few memories) resolves naturally as your corpus grows toward 1,000+ memories over 10 months.

The Stanford Generative Agents paper established the foundational formula still used across production systems:

```python
score = α_recency × recency + α_importance × importance + α_relevance × relevance
```

With all α values set to **1.0** and scores normalized to [0,1] using min-max scaling. Their reflection mechanism triggers higher-level memory consolidation when cumulative importance exceeds **150 points**—typically 2-3 times per simulated day.

---

## Multi-factor scoring grounded in cognitive science

ACT-R's base-level activation theory provides the mathematical foundation for memory salience. The decay equation `B_i = ln(Σ t_j^(-d))` with decay parameter **d = 0.5** reflects how memory strength follows a power law of forgetting—validated by Anderson & Schooler across email receipts, newspaper headlines, and natural language patterns.

**Recommended scoring factors with weights:**

```python
SALIENCE_WEIGHTS = {
    "novelty": 0.25,           # Computed via Neo4j vector similarity
    "emotional_intensity": 0.25, # Affective markers in content
    "actionability": 0.20,      # Tasks, commitments, decisions
    "domain_relevance": 0.20,   # Alignment with user's stated goals
    "temporal_significance": 0.10  # Deadlines, time-sensitive info
}
```

Behavioral tagging research from neuroscience (Frey & Morris, 1997) shows that emotionally salient events can "rescue" weak memories encoded within approximately **one hour before or after**. This suggests processing each 20-minute voice note as a holistic unit, allowing emotional peaks to elevate nearby mundane content.

The structured output schema should enforce type constraints at the API level:

```json
{
  "type": "object",
  "properties": {
    "overall_salience": {"type": "number", "minimum": 0, "maximum": 1},
    "factors": {
      "novelty": {"type": "number"},
      "emotional_intensity": {"type": "number"},
      "actionability": {"type": "number"}
    },
    "reasoning": {"type": "string"}
  },
  "required": ["overall_salience", "factors"]
}
```

---

## Real-world systems reveal proven patterns

**MemGPT/Letta** uses hierarchical memory with "cognitive triage"—the LLM itself decides what to store, summarize, or forget via tool calls (`core_memory_append`, `archival_memory_insert`). Rather than numerical scoring, it relies on context pressure warnings to trigger memory management, evaluating "potential future value" of information.

**Mem0** implements explicit priority scoring with dynamic forgetting: low-relevance entries decay over time while usage patterns, recency, and significance drive consolidation between short-term and long-term storage. Their graph-enhanced variant (Mem0g) stores memories as directed labeled graphs with entity extraction, relation generation, and conflict detection—reporting **26% accuracy improvement** over OpenAI's memory with **91% lower P95 latency**.

**OpenMemory (CaviraOSS)** uses a composite formula: `score = salience + recency + coactivation`. Its multi-sector architecture separates episodic, semantic, procedural, emotional, and reflective memories, each with adaptive decay rates rather than hard TTLs. The "waypoint" traces enable explainable recall.

**Obsidian Smart Connections** treats similarity scores as ranking signals rather than absolute grades—comparing scores within the same list, not across different notes. This relative approach prevents score inflation.

---

## PocketFlow pipeline for retrieve-score-create workflows

The optimal PocketFlow architecture uses BatchNode for parallel scoring of ~10 memories per voice note:

```python
from pocketflow import Node, BatchNode, Flow

class RetrieveSimilarNode(Node):
    """Query Neo4j for contextual memories."""
    def prep(self, shared):
        return shared["candidate_memories"]
    
    def exec(self, memories):
        embeddings = [m["embedding"] for m in memories]
        return neo4j_vector_search(embeddings, limit=5)
    
    def post(self, shared, prep_res, similar):
        shared["context"] = similar
        shared["novelty_scores"] = compute_novelty(
            shared["candidate_memories"], similar
        )
        return "score"

class ParallelScoreNode(BatchNode):
    """Score all memories concurrently."""
    def prep(self, shared):
        return list(zip(
            shared["candidate_memories"],
            shared["novelty_scores"]
        ))
    
    def exec(self, item):
        memory, novelty = item
        return suggest_salience(
            memory["content"],
            novelty_score=novelty,
            context=self.shared["context"]
        )
    
    def post(self, shared, prep_res, scores):
        shared["scored_memories"] = [
            {**m, "salience": s["score"]}
            for m, s in zip(shared["candidate_memories"], scores)
            if s["score"] >= 0.3  # Filter low-salience
        ]
        return "persist"
```

The shared store contract should include calibration state:

```python
shared = {
    "voice_note_text": "",
    "candidate_memories": [],
    "context": [],
    "novelty_scores": [],
    "historical_stats": {"mean": 0.5, "std": 0.15},
    "scored_memories": [],
    "calibration_window": deque(maxlen=200)
}
```

---

## Fast structured scoring with Groq and small model distillation

Groq's inference speed (**300-1,000+ tokens/second**) makes it ideal for real-time salience scoring. Using strict mode guarantees schema compliance:

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "salience_score",
            "strict": True,
            "schema": SALIENCE_SCHEMA
        }
    }
)
```

For edge deployment or cost reduction, distill to smaller models. The teacher-student approach:

1. Generate **1,000+ labeled examples** using GPT-4/Claude as teacher
2. Fine-tune **Phi-3-mini (3.8B)** or **Gemma 2 (2B)** with LoRA adapters
3. Train on both scores AND rationales ("distilling step-by-step")

Google Research showed this approach allows a **770M T5 model to match 540B PaLM** accuracy with only **12.5% of training data**. Phi-3-mini achieves strong classification performance with only **7.6M trainable parameters** via QLoRA.

The Instructor library provides reliable structured outputs with automatic retries:

```python
from pydantic import BaseModel, Field
import instructor

class SalienceScore(BaseModel):
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    factors: list[str]

client = instructor.from_provider("groq/llama-3.1-8b-instant")
result = client.create(
    messages=[{"role": "user", "content": f"Score: {memory}"}],
    response_model=SalienceScore,
    max_retries=3
)
```

---

## Neo4j graph patterns for salience propagation

Vector similarity search combined with graph traversal enables powerful retrieval-augmented scoring:

```cypher
// Find similar memories with graph context
CALL db.index.vector.queryNodes('memory-embeddings', 10, $queryEmbedding)
YIELD node AS seed, score
WITH seed, score
WHERE seed.salience > 0.3
MATCH (seed)-[r:RELATES_TO*1..2]-(related:Memory)
RETURN seed, related,
       (score * 0.6 + seed.salience * 0.4) AS combined_score
ORDER BY combined_score DESC
LIMIT 10
```

**PageRank for importance propagation** allows salience to flow through relationships:

```cypher
CALL gds.pageRank.stream('memory-graph', {
    maxIterations: 20,
    dampingFactor: 0.85,
    relationshipWeightProperty: 'weight'
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id AS memoryId,
       score AS propagatedSalience
```

The MERGE pattern for efficient upserts with conditional salience updates:

```cypher
MERGE (m:Memory {id: $memoryId})
ON CREATE SET
    m.content = $content,
    m.salience = $salience,
    m.embedding = $embedding,
    m.createdAt = datetime()
ON MATCH SET
    m.salience = CASE 
        WHEN $salience > m.salience THEN $salience 
        ELSE m.salience 
    END,
    m.lastAccessed = datetime(),
    m.accessCount = m.accessCount + 1
```

---

## Preventing calibration drift over 10 months

Score drift—where scores creep higher (inflation) or become too conservative (deflation)—undermines long-term quality. The solution combines rolling normalization with drift detection.

**Z-score normalization with 200-memory window:**

```python
class RollingCalibrator:
    def __init__(self, window_size=200, target_mean=0.5):
        self.history = deque(maxlen=window_size)
        self.target_mean = target_mean
    
    def calibrate(self, raw_score: float) -> float:
        self.history.append(raw_score)
        if len(self.history) < 20:
            return raw_score
        
        mean = np.mean(self.history)
        std = np.std(self.history) + 1e-8
        z_score = (raw_score - mean) / std
        
        # Sigmoid mapping to [0, 1]
        return 1 / (1 + np.exp(-z_score))
```

**CUSUM monitoring for drift detection:**

```python
class CUSUMMonitor:
    def __init__(self, target=0.5, threshold=5.0, slack=0.01):
        self.cumsum_pos = self.cumsum_neg = 0
        self.target, self.threshold, self.slack = target, threshold, slack
    
    def update(self, score: float) -> bool:
        deviation = score - self.target
        self.cumsum_pos = max(0, self.cumsum_pos + deviation - self.slack)
        self.cumsum_neg = max(0, self.cumsum_neg - deviation - self.slack)
        
        drift = self.cumsum_pos > self.threshold or self.cumsum_neg > self.threshold
        if drift:
            self.cumsum_pos = self.cumsum_neg = 0
        return drift
```

**The hybrid static-adaptive approach** resists drift by anchoring scores:

| Phase | Static Weight | Adaptive Weight | Rationale |
|-------|---------------|-----------------|-----------|
| Cold start (0-100 memories) | 0.8 | 0.2 | Limited data for adaptation |
| Growing (100-500) | 0.6 | 0.4 | Balanced learning |
| Mature (500+) | 0.5 | 0.5 | Full personalization |
| Drift detected | 0.8 | 0.2 | Reset to stable baseline |

---

## FastMCP tool implementation

The complete `suggest_salience` tool implementation for FastMCP:

```python
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

mcp = FastMCP("CognitiveMemory 🧠")

class SalienceResult(BaseModel):
    salience_score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    factors: dict
    calibration_applied: bool

@mcp.tool
async def suggest_salience(
    memory_content: str,
    memory_type: str = "general",
    ctx: Context = None
) -> SalienceResult:
    """
    Compute salience score for a voice note memory.
    Uses retrieval-augmented scoring against existing memory graph.
    """
    # Generate embedding
    embedding = await generate_embedding(memory_content)
    
    # Retrieve similar memories for novelty computation
    similar = await neo4j_search(embedding, limit=5)
    novelty = 1.0 - max(
        cosine_similarity(embedding, m["embedding"]) 
        for m in similar
    ) if similar else 1.0
    
    # Extract content features
    features = extract_features(memory_content)
    
    # Compute weighted score
    raw_score = (
        0.25 * novelty +
        0.25 * features["emotional_intensity"] +
        0.20 * features["actionability"] +
        0.20 * features["domain_relevance"] +
        0.10 * features["temporal_significance"]
    )
    
    # Apply calibration
    calibrated = calibrator.calibrate(raw_score)
    
    return SalienceResult(
        salience_score=round(calibrated, 3),
        confidence=compute_confidence(features, len(similar)),
        factors={"novelty": novelty, **features},
        calibration_applied=True
    )
```

---

## Quality metrics for long-term validation

Track these metrics to validate that salience scoring improves retrieval quality over time:

**Retrieval metrics:**
- **Precision@5**: Are the top 5 retrieved memories truly relevant? (Target: >0.7)
- **NDCG@10**: Does ranking quality hold at deeper depths?
- **Hit Rate@K**: Binary success for specific queries

**Calibration metrics:**
- **Expected Calibration Error (ECE)**: Do predicted scores match actual importance? (Target: <0.1)
- **Brier Score**: Mean squared error of probabilistic predictions
- **Score distribution entropy**: Should remain stable month-over-month

**Feedback loops:**
- Track which memories are re-accessed (validates high salience)
- Monitor memories never retrieved (candidates for recalibration)
- Allow explicit user marking of importance

The compounding effect emerges from the retrieval-augmented pattern: as your memory graph grows, novelty computation becomes increasingly accurate, graph-based salience propagation captures implicit importance through relationship density, and calibration stabilizes with more training examples.

---

## Conclusion

Building a salience scoring system that compounds quality over 1,000+ memories requires three architectural decisions: **retrieval-augmented scoring** that grounds novelty in actual graph comparison rather than LLM estimation, **hybrid static-adaptive weights** that resist calibration drift while enabling personalization, and **structured outputs** that eliminate parsing brittleness. The PocketFlow retrieve-score-create pipeline, combined with Neo4j's vector indexes and PageRank propagation, provides the infrastructure. Groq enables fast production scoring while distillation to Phi-3/Gemma offers edge deployment options. The key insight from cognitive science—that emotional salience, novelty, and rehearsal frequency jointly determine memory strength—translates directly into a multi-factor scoring formula that improves as your graph densifies.