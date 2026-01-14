# Phase 6: User Stories

> **Purpose**: Concrete scenarios that Phase 6 `query_memories` feature should enable

---

## User Story 1: Natural Language Q&A

### The Scenario

**Context**: I've stored multiple memories about a meeting with Alice from FastTrack:

```
Memory 1: "Met with Alice from FastTrack on 2026-01-10 to discuss N8N workflow automation"
Memory 2: "Alice's budget is €60/hour, 20 hours approved for N8N project"
Memory 3: "N8N project starts Monday January 13, 2026"
```

**My question**:
> "When did I meet with Alice?"

**Without Phase 6**:
- `get_memory("Alice")` returns all 3 memories as raw text
- I have to scan through them to find the date
- No direct answer provided

**With Phase 6**:
```
## Answer
You met with Alice on January 10, 2026, to discuss the N8N workflow
integration for the FastTrack project.

## Reasoning
Found memory [1] which records the meeting on 2026-01-10 about N8N workflow
with Alice from FastTrack. The meeting was documented as an Episodic memory
with high salience (0.85), indicating it was important.

## Confidence
0.92 / 1.0 (Very Confident)

## Sources
1 memory entries used
```

### Acceptance Criteria

- [ ] Natural language question returns direct answer (not raw memories)
- [ ] Answer is 2-4 sentences, human-readable
- [ ] Reasoning explains which memories informed the answer
- [ ] Confidence score reflects certainty (0.9+ for direct matches)
- [ ] Response includes number of memories used

---

## User Story 2: Decision Rationale Queries

### The Scenario

**Context**: I stored technology decisions with rationale:

```
Memory 1: "Chose PostgreSQL over MongoDB for FastTrack project"
Memory 2: "PostgreSQL needed for ACID compliance with financial transactions"
Memory 3: "FastTrack requires reliable transaction processing"
Memory 4: "Mongodb considered but rejected due to lack of native transactions"
```

**My question**:
> "Why did I choose PostgreSQL over MongoDB?"

**Without Phase 6**:
- `get_memory_relations("PostgreSQL")` returns themes and insights
- I get structured data but no synthesized answer
- I have to piece together the rationale myself

**With Phase 6**:
```
## Answer
You chose PostgreSQL over MongoDB primarily for ACID compliance and transactional
integrity, which were critical for the financial data processing requirements
of the FastTrack project.

## Reasoning
Analyzed 3 memories:
- Memory [1] (Semantic, salience 0.90): Documents the decision stating "ACID
  compliance was non-negotiable for financial transactions"
- Memory [2] (Semantic, salience 0.75): Notes that MongoDB was considered but
  rejected due to "lack of native transaction support at the time"
- Memory [3] (Reflective, salience 0.70): Post-decision reflection confirming
  the choice was correct: "PostgreSQL has scaled well"

The decision was driven by technical requirements (ACID compliance) rather
than cost or familiarity.

## Confidence
0.88 / 1.0 (Confident)

## Sources
3 memory entries used
```

### Acceptance Criteria

- [ ] "Why" questions synthesize rationale from multiple memories
- [ ] Reasoning traces through each relevant memory
- [ ] Answer explains the decision-making process
- [ ] Memory references use [1], [2] notation for traceability
- [ ] Confidence reflects strength of evidence

---

## User Story 3: Summary Queries

### The Scenario

**Context**: I've had multiple interactions with FastTrack client:

```
Memory 1: "Initial meeting with FastTrack: Discussed N8N workflow automation scope"
Memory 2: "FastTrack budget: €60/hour, 20 hours approved"
Memory 3: "FastTrack project starts Monday January 13"
Memory 4: "Follow-up call: FastTrack wants to expand scope to include CRM integration"
Memory 5: "FastTrack deal closed: €1200 total for initial phase"
```

**My question**:
> "Summarize my work with FastTrack"

**Without Phase 6**:
- `get_all_memories()` returns everything, FastTrack mixed with other projects
- `get_memory("FastTrack")` returns 5 raw memories
- No synthesis or organization

**With Phase 6**:
```
## Answer
Your FastTrack engagement involves N8N workflow automation with an initial budget
of €1,200 (€60/hour × 20 hours). The project started January 13, 2026, and has
since expanded to include CRM integration. The initial phase is complete with the
deal closed at the original agreed price.

## Reasoning
Synthesized from 5 memories grouped into themes:

**Project Scope**:
- Memory [1]: Initial N8N workflow automation (Episodic, salience 0.80)
- Memory [4]: Expanded to CRM integration (Episodic, salience 0.75)

**Financial**:
- Memory [2]: Budget €60/hour, 20 hours approved (Semantic, salience 0.85)
- Memory [5]: Deal closed at €1,200 (Semantic, salience 0.90)

**Timeline**:
- Memory [3]: Project started January 13, 2026 (Episodic, salience 0.70)

## Confidence
0.85 / 1.0 (Confident)

## Sources
5 memory entries used
```

### Acceptance Criteria

- [ ] "Summarize" queries aggregate multiple memories
- [ ] Results organized by theme (scope, financial, timeline)
- [ ] Answer provides high-level overview with key details
- [ ] All relevant memories included in synthesis
- [ ] Confidence reflects completeness of summary

---

## User Story 4: Complex Multi-Hop Queries

### The Scenario

**Context**: Interconnected memories across different domains:

```
Memory 1: "FastTrack uses PostgreSQL for production database"
Memory 2: "PostgreSQL chosen for ACID compliance requirements"
Memory 3: "FastTrack processes financial transactions"
Memory 4: "N8N workflow needs to query FastTrack database"
Memory 5: "N8N uses PostgreSQL connector for database access"
```

**My question**:
> "What database does N8N use to connect to FastTrack data?"

**Without Phase 6**:
- Simple keyword search for "N8N database" returns Memory 5 only
- Misses the connection chain: N8N → PostgreSQL → FastTrack
- Incomplete answer

**With Phase 6** (with Reflection Node):
```
## Answer
N8N uses the PostgreSQL connector to access the FastTrack production database,
which is PostgreSQL. This connection is necessary because FastTrack processes
financial transactions requiring ACID compliance.

## Reasoning
**Initial retrieval** found 2 memories:
- Memory [5]: "N8N uses PostgreSQL connector" (direct match)

**Reflection phase** identified gap:
- Missing: Why does N8N connect to PostgreSQL?

**Additional retrieval** found:
- Memory [1]: "FastTrack uses PostgreSQL"
- Memory [3]: "FastTrack processes financial transactions"
- Memory [2]: "PostgreSQL chosen for ACID compliance"

**Chain**: N8N → PostgreSQL connector → FastTrack PostgreSQL → ACID requirements

## Confidence
0.82 / 1.0 (Confident)

## Sources
4 memory entries used (2 initial + 2 via reflection)
```

### Acceptance Criteria

- [ ] Complex queries trigger reflection when initial results are sparse
- [ ] Reflection identifies information gaps
- [ ] Additional retrieval fills gaps with related concepts
- [ ] Reasoning explains the multi-hop connection chain
- [ ] Confidence adjusted for complexity (penalty for indirect matches)

---

## User Story 5: Handling Uncertainty

### The Scenario

**Context**: Limited or ambiguous information:

```
Memory 1: "Discussed pricing with client, maybe around €50-80/hour"
Memory 2: "Client meeting in early January, date uncertain"
```

**My question**:
> "What's the agreed rate with this client?"

**Without Phase 6**:
- Returns raw memory with "maybe", "uncertain"
- No quantification of uncertainty
- User has to interpret ambiguity

**With Phase 6**:
```
## Answer
Based on available information, the client rate appears to be in the €50-80/hour
range, but this is not definitively confirmed. The exact rate may need to be
clarified with the client.

## Reasoning
Found only 1 relevant memory:
- Memory [1]: Mentions "maybe around €50-80/hour" (Episodic, salience 0.50)

**Uncertainty factors**:
- Memory uses hedge words ("maybe", "around")
- No confirmed rate documented
- Low salience (0.50) suggests this was preliminary

## Confidence
0.35 / 1.0 (Low)

### Note
This information is uncertain. Consider:
- Checking contract documentation
- Confirming rate with client
- Creating a new memory once rate is confirmed

## Sources
1 memory entries used
```

### Acceptance Criteria

- [ ] Low confidence (<0.5) explicitly marked
- [ ] Reasoning explains why confidence is low
- [ ] Answer includes uncertainty caveats
- [ ] Suggestions provided for improving confidence
- [ ] Hedge words ("maybe", "possibly") penalize confidence score

---

## User Story 6: No Results with Guidance

### The Scenario

**Context**: No memories match the query

**My question**:
> "What did we decide about the API gateway?"

**Without Phase 6**:
- Returns "No memories found"
- No guidance on what to do next
- Dead end

**With Phase 6**:
```
## Answer
I couldn't find any relevant memories to answer your question about API gateway
decisions.

## Reasoning
Searched for memories matching: "API gateway", "API", "gateway"
- No results found in any sector
- No related concepts matched

## Confidence
0.0 / 1.0 (Uncertain)

## Sources
0 memory entries used

### Suggestions
- Try using get_memory with different keywords (e.g., "API", "gateway", "routing")
- Check if memories exist with get_all_memories
- Consider creating a new memory about the API gateway decision
- Try get_memory_relations for broader context
```

### Acceptance Criteria

- [ ] Empty results return helpful message (not just "not found")
- [ ] Suggest alternative search strategies
- [ ] Recommend related tools to try
- [ ] Confidence score is 0.0 for no results
- [ ] User knows next steps to take

---

## User Story 7: Opinion/Attitude Queries

### The Scenario

**Context**: Stored memories include subjective assessments:

```
Memory 1: "Alice from FastTrack is technically knowledgeable but budget-conscious"
Memory 2: "FastTrack project is challenging but rewarding"
Memory 3: "Alice likes the N8N approach, finds it innovative"
```

**My question**:
> "What does Alice think about the project?"

**Without Phase 6**:
- Returns all 3 memories
- No synthesis of Alice's attitude
- User has to infer opinion themselves

**With Phase 6**:
```
## Answer
Alice views the N8N workflow automation project positively, finding the approach
innovative. While she is budget-conscious, she appears technically supportive
of the implementation.

## Reasoning
Analyzed 3 memories for sentiment and attitude:
- Memory [1]: Alice is "technically knowledgeable but budget-conscious"
  → Neutral to positive technical assessment
- Memory [2]: Project is "challenging but rewarding"
  → Context for project difficulty
- Memory [3]: Alice "likes the N8N approach, finds it innovative"
  → Direct positive opinion

**Key sentiment indicators**:
- "likes", "innovative" → positive
- "technically knowledgeable" → professional respect
- "budget-conscious" → pragmatic concern

## Confidence
0.78 / 1.0 (Confident)

## Sources
3 memory entries used
```

### Acceptance Criteria

- [ ] Opinion queries synthesize sentiment from multiple memories
- [ ] Answer distinguishes fact vs opinion
- [ ] Reasoning includes sentiment indicators found
- [ ] Confidence reflects clarity of opinion (ambiguous sentiments lower confidence)
- [ ] Subjective nature of answer acknowledged

---

## User Story 8: Temporal Queries

### The Scenario

**Context**: Memories with timestamps:

```
Memory 1: "Met with Alice on January 10, 2026" (created: 2026-01-10)
Memory 2: "Follow-up call scheduled for January 20, 2026" (created: 2026-01-10)
Memory 3: "Project starts January 13, 2026" (created: 2026-01-08)
```

**My question**:
> "What are my upcoming FastTrack deadlines?"

**Without Phase 6**:
- Returns all memories chronologically
- No distinction between past and future
- User has to calculate dates themselves

**With Phase 6**:
```
## Answer
You have one upcoming FastTrack deadline:
- **January 20, 2026**: Follow-up call with Alice

Recent milestones:
- January 13, 2026: Project start date (past)
- January 10, 2026: Initial meeting (past)

## Reasoning
Filtered 3 memories by temporal relevance:
- Memory [2]: Follow-up January 20, 2026 → UPCOMING
- Memory [3]: Project start January 13 → PAST (3 days ago)
- Memory [1]: Meeting January 10 → PAST (6 days ago)

Current date: 2026-01-16

## Confidence
0.95 / 1.0 (Very Confident)

## Sources
3 memory entries used
```

### Acceptance Criteria

- [ ] Temporal queries ("upcoming", "recent", "past") filter appropriately
- [ ] Answer distinguishes past vs future clearly
- [ ] Relative time references ("3 days ago") included
- [ ] Confidence high for precise temporal data
- [ ] Current date used for context

---

## Prioritization

| User Story | Priority | Complexity | Dependencies |
|------------|----------|------------|--------------|
| US1: Natural Language Q&A | P0 (Must-have) | Medium | Query analysis, synthesis |
| US2: Decision Rationale | P0 (Must-have) | High | Multi-memory synthesis |
| US3: Summary Queries | P0 (Must-have) | Medium | Thematic grouping |
| US4: Multi-Hop Queries | P1 (Should-have) | High | Reflection node |
| US5: Handling Uncertainty | P1 (Should-have) | Medium | Confidence calculation |
| US6: No Results Guidance | P1 (Should-have) | Low | Error handling |
| US7: Opinion Queries | P2 (Nice-to-have) | High | Sentiment analysis |
| US8: Temporal Queries | P2 (Nice-to-have) | Medium | Date parsing |

**Phase 6 MVP**: Focus on US1, US2, US3, US5, US6

**Phase 6+**: US4, US7, US8

---

## Testing Scenarios

### Scenario 1: Simple Factual Query

1. Store memory: "Met with Alice on 2026-01-10"
2. Ask: "When did I meet with Alice?"
3. Verify: Direct answer returned with confidence >0.9
4. Verify: Reasoning includes memory reference

### Scenario 2: Complex Rationale Query

1. Store decision + 2 supporting memories
2. Ask: "Why did I choose X over Y?"
3. Verify: Synthesis combines all 3 memories
4. Verify: Reasoning traces decision chain

### Scenario 3: No Results

1. Ask question with no matching memories
2. Verify: Helpful error message returned
3. Verify: Suggestions for next steps provided
4. Verify: Confidence score is 0.0

### Scenario 4: Low Confidence

1. Store memory with hedge words ("maybe", "possibly")
2. Ask factual question about that memory
3. Verify: Confidence score <0.5
4. Verify: Uncertainty acknowledged in response

---

**End of User Stories**
