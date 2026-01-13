# Phase 3: Voice Memo Processing & Advanced Workflows
**Goal**: Process 15-minute voice memos → Create multiple memories in Neo4j + Obsidian with AI agents

---

## Overview

Phase 3 brings advanced AI workflows to Brain OS + Obsidian integration. Users can record voice memos, and Brain OS automatically:
1. Transcribes audio (Whisper API)
2. Extracts entities (Groq)
3. Segments content into multiple memories (Groq)
4. Generates observations (OpenRouter)
5. Creates memories in Neo4j + Obsidian
6. Updates daily notes in Obsidian
7. Creates relationships in graph view

**Success Criteria**:
- ✅ Voice memo → 3-5 memories created automatically
- ✅ Daily note updated with memo summary
- ✅ Entities linked in Obsidian graph view
- ✅ Cognitive balance indicators in daily notes
- ✅ Weekly review workflow includes Obsidian data

**Out of Scope**:
- ❌ Real-time audio streaming (batch processing only)
- ❌ Mobile app integration (Phase 4+)
- ❌ Video processing (audio only)

---

## User Stories

**Note**: Claude handles audio transcription via MCP, so we only process already-transcribed text.

### Story 1: Extract Entities from Transcript

**As a** Brain OS system
**I want to** extract named entities from transcripts
**So that** I can tag memories and create relationships

**Acceptance Criteria**:
- [ ] New flow: `entity_extraction_flow` (PocketFlow)
- [ ] Uses Groq (fast ~100-200ms)
- [ ] Extracts: People, Projects, Technologies, Companies, Dates
- [ ] Returns list of entities with types
- [ ] Deduplicates entities (case-insensitive)
- [ ] Limits to top 10 most relevant entities

**Technical Implementation**:
```python
# src/flows/entity_extraction.py
from pocketflow import AsyncNode, AsyncFlow
from src.utils.llm import get_groq_client

class ExtractEntitiesNode(AsyncNode):
    async def exec_async(self, inputs):
        text = inputs["text"]

        groq = get_groq_client()
        response = groq.chat.completions.create(
            model=os.getenv("GROQ_QUICK_MODEL"),
            messages=[
                {"role": "system", "content": "Extract named entities: people, projects, technologies, companies. Return JSON array."},
                {"role": "user", "content": text}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        entities = json.loads(response.choices[0].message.content)
        return entities["entities"][:10]  # Top 10

entity_extraction_flow = AsyncFlow(start=ExtractEntitiesNode())
```

---

### Story 3: Segment Transcript into Multiple Memories

**As a** Brain OS system
**I want to** segment long transcripts into logical memories
**So that** each memory has a clear topic and sector

**Acceptance Criteria**:
- [ ] New flow: `content_segmentation_flow` (PocketFlow)
- [ ] Uses Groq (fast ~300ms)
- [ ] Segments transcript by:
  - Topic changes (meeting → decision → next steps)
  - Cognitive sector (Episodic, Semantic, Procedural, Emotional)
- [ ] Each segment includes:
  - `content`: Summary of segment
  - `sector`: Cognitive classification
  - `entities`: Relevant entities
  - `salience`: Importance score (0.0-1.0)
  - `memory_type`: instinctive, thinking, or dormant
- [ ] Returns 3-5 segments per 15-minute memo

**Technical Implementation**:
```python
# src/flows/content_segmentation.py
class SegmentContentNode(AsyncNode):
    async def exec_async(self, inputs):
        text = inputs["text"]
        entities = inputs["entities"]

        groq = get_groq_client()
        response = groq.chat.completions.create(
            model=os.getenv("GROQ_QUICK_MODEL"),
            messages=[
                {"role": "system", "content": """Segment transcript into 3-5 logical memories.
For each memory:
- content: 2-3 sentence summary
- sector: Episodic|Semantic|Procedural|Emotional|Reflective
- entities: list of relevant entities
- salience: 0.0-1.0 (0.9+=critical, 0.7-0.8=important, 0.5-0.6=routine)
- memory_type: instinctive (if foundational decision), thinking (default), dormant (if historical)
Return JSON array."""},
                {"role": "user", "content": f"Transcript:\n{text}\n\nEntities:\n{entities}"}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)["segments"]

segmentation_flow = AsyncFlow(start=SegmentContentNode())
```

---

### Story 4: Generate Observations for Each Segment

**As a** Brain OS system
**I want to** generate contextual observations for each memory
**So that** memories have detailed rationale and context

**Acceptance Criteria**:
- [ ] New flow: `observation_generation_flow` (PocketFlow)
- [ ] Uses OpenRouter (deep thinking ~2-3s per segment)
- [ ] For each segment:
  - Generates 3-5 observations
  - Includes: rationale, alternatives, trade-offs, deadlines, context
- [ ] Observations are specific, not generic
- [ ] Total time: ~10-15s for 5 segments

**Technical Implementation**:
```python
# src/flows/observation_generation.py
class GenerateObservationsNode(AsyncNode):
    async def exec_async(self, inputs):
        segment = inputs["segment"]
        full_transcript = inputs["full_transcript"]

        openrouter = await get_openrouter_client()
        response = await openrouter.chat.completions.create(
            model=os.getenv("OPENROUTER_THINKING_MODEL"),
            messages=[
                {"role": "system", "content": """Generate 3-5 observations for this memory segment.
Observations should include:
- Decision rationale (WHY, not just WHAT)
- Alternatives considered
- Trade-offs made
- Deadlines or time constraints
- Key context from transcript

Be specific, not generic."""},
                {"role": "user", "content": f"Segment: {segment['content']}\n\nFull context: {full_transcript[:1000]}"}
            ],
            temperature=0.5,
            max_tokens=500
        )

        return response.choices[0].message.content.split("\n")

observation_flow = AsyncFlow(start=GenerateObservationsNode())
```

---

### Story 4: Process Voice Memo Tool

**As a** Brain OS user
**I want** a single tool to process voice memo transcripts end-to-end
**So that** I can easily create multiple memories from transcribed text

**Acceptance Criteria**:
- [ ] New tool: `process_voice_memo(transcript: str, source: str = "voice_memo")`
- [ ] Accepts already-transcribed text (Claude handles transcription via MCP)
- [ ] Pipeline:
  1. Extract entities (Groq)
  2. Segment content (Groq)
  3. Generate observations per segment (OpenRouter)
  4. Create memories in Neo4j (parallel)
  5. Create entities in Obsidian (parallel)
  6. Create relationships in Obsidian
  7. Update daily note
- [ ] Returns summary: "{N} memories created from voice memo"
- [ ] Progress logging at each step
- [ ] Total time: ~20-30s for 15-minute transcript

**Technical Implementation**:
```python
# src/tools/memory/voice_memo.py
@mcp.tool
async def process_voice_memo(
    transcript: str = Field(description="Transcribed text from voice memo (already transcribed by Claude)"),
    source: str = Field(default="voice_memo", description="Source identifier")
) -> str:
    """Process voice memo transcript: segment, create memories in Neo4j + Obsidian."""

    # Step 1: Extract entities
    logger.info("Extracting entities...")
    entities = await entity_extraction_flow.run_async({"text": transcript})

    # Step 3: Segment content
    logger.info("Segmenting content...")
    segments = await segmentation_flow.run_async({
        "text": transcript,
        "entities": entities
    })

    # Step 4: Generate observations for each segment
    logger.info(f"Generating observations for {len(segments)} segments...")
    for segment in segments:
        observations = await observation_flow.run_async({
            "segment": segment,
            "full_transcript": transcript
        })
        segment["observations"] = observations

    # Step 5: Create memories in Neo4j + Obsidian (parallel)
    logger.info("Creating memories...")
    created_memories = []

    for segment in segments:
        # Create in Neo4j
        bubble_id = await upsert_bubble(
            content=segment["content"],
            sector=segment["sector"],
            entities=segment["entities"],
            observations=segment["observations"],
            salience=segment["salience"],
            memory_type=segment["memory_type"],
            source=source
        )

        # Create in Obsidian
        async with get_obsidian_client() as obsidian:
            entity_name = generate_entity_name(segment["content"], segment["entities"])
            await obsidian.call_tool("create_entities", {
                "name": entity_name,
                "entityType": segment["sector"],
                "observations": segment["observations"],
                "metadata": {
                    "neo4j_id": bubble_id,
                    "salience": segment["salience"],
                    "memory_type": segment["memory_type"],
                    "source": source,
                    "created": datetime.now().isoformat()
                }
            })

            created_memories.append({
                "neo4j_id": bubble_id,
                "obsidian_entity": entity_name,
                "sector": segment["sector"]
            })

    # Step 6: Create relationships
    logger.info("Creating entity relationships...")
    await create_cross_entity_relations(created_memories)

    # Step 7: Update daily note
    logger.info("Updating daily note...")
    await update_daily_note_with_voice_memo(created_memories, transcript[:200])

    return f"""
    ✅ Voice memo processed successfully!

    Created {len(created_memories)} memories:
    {format_memory_summary(created_memories)}

    Open Obsidian to explore relationships in graph view.
    """
```

---

### Story 5: Update Daily Note with Voice Memo Summary

**As a** Brain OS user
**I want** daily notes updated when I process voice memos
**So that** I have a chronological record of my voice inputs

**Acceptance Criteria**:
- [ ] New function: `update_daily_note_with_voice_memo(memories, transcript_snippet)`
- [ ] Daily note format: `daily/YYYY-MM-DD.md`
- [ ] Appends section:
  ```
  ### Voice Memo (HH:MM)
  - [[Memory 1]] (Semantic, salience 0.85)
  - [[Memory 2]] (Episodic, salience 0.6)
  - [[Memory 3]] (Procedural, salience 0.7)

  Snippet: "Discussed Project X database decision..."
  ```
- [ ] Creates daily note if doesn't exist
- [ ] Uses Templater template if available

**Technical Implementation**:
```python
# src/utils/daily_notes.py
async def update_daily_note_with_voice_memo(memories, transcript_snippet):
    """Append voice memo summary to today's daily note."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_note_path = f"{os.getenv('OBSIDIAN_VAULT_PATH')}/daily/{today}.md"

    # Create note if doesn't exist
    if not os.path.exists(daily_note_path):
        await create_daily_note(today)

    # Append voice memo section
    with open(daily_note_path, 'a', encoding='utf-8') as f:
        f.write(f"\n### Voice Memo ({datetime.now().strftime('%H:%M')})\n")
        for mem in memories:
            f.write(f"- [[{mem['obsidian_entity']}]] ({mem['sector']}, salience {mem.get('salience', 0.5)})\n")
        f.write(f"\nSnippet: \"{transcript_snippet}...\"\n")
```

---

### Story 6: Create Daily Note Template

**As a** Brain OS user
**I want** daily notes with consistent structure and Brain OS data
**So that** I have a complete daily overview

**Acceptance Criteria**:
- [ ] Template file: `templates/daily-note.md`
- [ ] Sections:
  - Date metadata (YAML frontmatter)
  - Brain OS Snapshot (sector balance, active projects)
  - Today's Memories Created
  - Voice Memos
  - Instinctive Activations
  - Weekly Goals Progress
  - Cognitive Balance Note
- [ ] Auto-populated via `create_daily_note(date)` function
- [ ] Templater compatible (if user has plugin)

**Template Example**:
```markdown
---
date: {{date}}
day: {{day_name}}
week: {{week_number}}
---

# {{day_name}}, {{date_formatted}}

## Brain OS Snapshot
- **Active Projects**: {{active_projects_count}}
- **Sector Balance**: {{sector_distribution}}
- **Instinctive Memories**: {{instinctive_count}} active
- **Total Memories**: {{total_count}}

## Today's Memories Created

### Morning (9:00-12:00)

### Afternoon (13:00-17:00)

### Evening (17:00-21:00)

## Voice Memos

## Instinctive Activations
When I thought about "{{context}}", Brain OS auto-activated:

## Weekly Goals Progress
- [ ] Goal 1
- [ ] Goal 2

## Cognitive Balance Note
{{cognitive_balance_warning}}
```

---

### Story 7: Weekly Review with Obsidian Data

**As a** Brain OS user
**I want** weekly reviews to include Obsidian insights
**So that** I can see both graph patterns and quantitative data

**Acceptance Criteria**:
- [ ] Enhanced tool: `weekly_review_with_obsidian()`
- [ ] Combines data:
  - Neo4j: Sector balance, salience trends, access counts
  - Obsidian: Entity relationships, graph patterns, daily note summaries
- [ ] Generates Reflective memory with:
  - Key themes from week
  - Sector imbalances to address
  - Most connected entities (graph centrality)
  - Suggested actions for next week
- [ ] Creates `daily/YYYY-WXX-Review.md` in Obsidian

**Technical Implementation**:
```python
@mcp.tool
async def weekly_review_with_obsidian() -> str:
    """Generate weekly review combining Neo4j + Obsidian data."""

    # Step 1: Get Neo4j data
    memories_this_week = await get_all_bubbles(limit=100)  # Filter by date
    sector_balance = calculate_sector_distribution(memories_this_week)

    # Step 2: Get Obsidian graph data
    async with get_obsidian_client() as obsidian:
        graph = await obsidian.call_tool("read_graph", {})
        # Analyze graph centrality, most connected entities
        central_entities = analyze_graph_centrality(graph)

    # Step 3: Generate synthesis (OpenRouter)
    synthesis = await synthesize_weekly_review(
        memories_this_week,
        sector_balance,
        central_entities
    )

    # Step 4: Create Reflective memory
    bubble_id = await upsert_bubble(
        content=synthesis,
        sector="Reflective",
        memory_type="thinking",
        salience=0.75,
        source="weekly_review"
    )

    # Step 5: Create weekly review note in Obsidian
    week_number = datetime.now().strftime("%Y-W%W")
    await create_weekly_review_note(week_number, synthesis, sector_balance, central_entities)

    return f"✅ Weekly review complete: {synthesis[:200]}..."
```

---

## Technical Requirements

### Dependencies

**Python (Brain OS)**:
- Existing: `groq`, `openai` (for OpenRouter)
- No new dependencies needed (Claude handles transcription)

### File Changes

**New Files**:
- `src/flows/entity_extraction.py` - Entity extraction flow
- `src/flows/content_segmentation.py` - Content segmentation flow
- `src/flows/observation_generation.py` - Observation generation flow
- `src/tools/memory/voice_memo.py` - Voice memo processing tool
- `src/utils/daily_notes.py` - Daily note management utilities
- `templates/daily-note.md` - Daily note template
- `docs/project/phase4/phase3_user_stories.md` - This document

**Modified Files**:
- `src/tools/agents/summarize_project.py` - Enhance with Obsidian data
- `brainos_server.py` - Register voice memo tool

### Environment Variables

```env
# Obsidian Vault
OBSIDIAN_VAULT_PATH=/home/user/brain-os-vault

# Note: No OpenAI key needed - Claude handles transcription
```

---

## Testing Plan

### Unit Tests

1. **Test Entity Extraction**:
   - Sample transcript → list of entities
   - Verify: people, projects, technologies detected
   - Check deduplication

2. **Test Content Segmentation**:
   - 500-word transcript → 3-5 segments
   - Verify each has: content, sector, entities, salience
   - Check segment boundaries make sense

### Integration Tests

1. **Test End-to-End Voice Memo**:
   - 15-minute transcript → process_voice_memo(transcript)
   - Verify: 3-5 memories in Neo4j
   - Verify: 3-5 entities in Obsidian
   - Verify: Daily note updated
   - Verify: Graph view shows relationships
   - Total time < 60 seconds

2. **Test Daily Note Updates**:
   - Process 2 voice memos same day
   - Verify: Both appended to same daily note
   - Verify: Chronological order (by HH:MM)

3. **Test Weekly Review**:
   - Create 20 memories over 7 days
   - Run weekly_review_with_obsidian()
   - Verify: Synthesis includes Neo4j + Obsidian data
   - Verify: Weekly review note created

---

## Success Metrics

**Phase 3 Complete When**:
- ✅ 15-minute voice memo → 3-5 memories created
- ✅ All memories appear in Neo4j + Obsidian
- ✅ Daily note updated with voice memo summary
- ✅ Entity relationships visible in graph view
- ✅ Weekly review includes Obsidian insights
- ✅ Total processing time < 60 seconds

**User Acceptance**:
- ✅ User records voice memo, Claude transcribes it via MCP
- ✅ User sends transcribed text to `process_voice_memo(transcript)`
- ✅ User opens Obsidian, sees new entities
- ✅ User checks daily note, sees summary
- ✅ User explores graph view, sees relationships
- ✅ User confirms "Voice memo workflow works perfectly"

---

## Out of Scope (Future Phases)

**NOT in Phase 3**:
- ❌ Real-time audio streaming (batch processing only)
- ❌ Mobile app integration (desktop only)
- ❌ Video processing (audio only)
- ❌ Speaker diarization (who said what)
- ❌ Automatic voice memo detection (manual trigger only)
- ❌ Multi-language support (English only for now)

---

## Estimated Effort

| Story | Complexity | Effort |
|-------|------------|--------|
| Story 1: Entity Extraction | Medium | 3 hours |
| Story 2: Content Segmentation | High | 5 hours |
| Story 3: Observation Generation | Medium | 3 hours |
| Story 4: Voice Memo Tool | High | 6 hours |
| Story 5: Daily Note Updates | Medium | 3 hours |
| Story 6: Daily Note Template | Low | 2 hours |
| Story 7: Weekly Review Enhancement | Medium | 4 hours |

**Total Estimated Effort**: 26 hours

**Timeline**: 3-4 days of focused development

---

## Next Steps After Phase 3 Approval

1. User reviews Phase 3 user stories
2. User approves Phase 3 scope
3. I implement after Phase 2 completion
4. User tests with real 15-minute voice memo
5. User approves Phase 3 completion
6. Brain OS + Obsidian integration COMPLETE! 🎉

---

**Phase 3 Status**: ⏳ Awaiting User Approval (after Phase 2)
**Dependencies**: Phase 1 and Phase 2 must be completed first
**Next Action**: User reviews Phase 3 user stories
