# Phase 3: Scheduled Recurring Updates
**Goal**: Automated daily and weekly updates sent to Obsidian at configurable times

---

## Overview

Phase 3 brings automated, scheduled updates to Brain OS + Obsidian integration. Instead of manual triggers, the system automatically generates and sends:
- **Morning Briefing** (configurable time, default 7:00 AM)
- **Evening Recap** (configurable time, default 7:00 PM)
- **Sunday Weekly Review** (configurable time, default 7:00 AM, skips Saturday)

Each update creates a structured note in Obsidian with Brain OS insights, memory summaries, and cognitive balance metrics.

**Success Criteria**:
- ✅ Morning briefing automatically created at scheduled time
- ✅ Evening recap automatically created at scheduled time
- ✅ Sunday weekly review automatically created (skip Saturday)
- ✅ All times configurable via environment variables
- ✅ Updates contain Neo4j insights + Obsidian context
- ✅ Graceful handling if Obsidian unavailable

**Out of Scope**:
- ❌ Voice memo processing (removed from scope)
- ❌ Transcript processing (removed from scope)
- ❌ Entity extraction (removed from scope)

---

## User Stories

### Story 1: Morning Briefing Update

**As a** Brain OS user
**I want to** receive an automated morning briefing every day
**So that** I start my day with context from my memories

**Acceptance Criteria**:
- [ ] New background task: `morning_briefing_task`
- [ ] Runs daily at configurable time (default: 07:00)
- [ ] Creates daily note: `daily/YYYY-MM-DD.md`
- [ ] Includes sections:
  - **Morning Briefing** header with timestamp
  - **Yesterday's Recap**: Top 5 memories from yesterday
  - **Today's Focus**: Instinctive memories that may activate today
  - **Active Projects**: Current projects with recent activity
  - **Cognitive Balance**: Sector distribution check
- [ ] Uses OpenRouter Creative model for synthesis
- [ ] Configurable via env var: `MORNING_BRIEFING_TIME` (format: "HH:MM", default: "07:00")
- [ ] Graceful fallback if Obsidian unavailable

**Morning Briefing Format**:
```markdown
## Morning Briefing (07:00)

### Yesterday's Recap
Top memories from yesterday:
- [[PostgreSQL Decision]] - Database choice for Project X
- [[FastTrack Meeting]] - N8N workflow discussion
- [[Code Review Notes]] - API gateway patterns

### Today's Focus
Memories that may activate based on context:
- Project X deployment (salience 0.9, last accessed 3 days ago)
- FastTrack follow-up (salience 0.8, instinctive)

### Active Projects
- **Project X**: 12 memories, last activity yesterday
- **FastTrack Client**: 8 memories, last activity 2 days ago

### Cognitive Balance
Current distribution: Episodic 35%, Semantic 40%, Procedural 15%, Emotional 5%, Reflective 5%
✅ Healthy balance - consider adding Emotional memories
```

---

### Story 2: Evening Recap Update

**As a** Brain OS user
**I want to** receive an automated evening recap every night
**So that** I end my day with a summary of what I accomplished

**Acceptance Criteria**:
- [ ] New background task: `evening_recap_task`
- [ ] Runs daily at configurable time (default: 19:00)
- [ ] Appends to existing daily note: `daily/YYYY-MM-DD.md`
- [ ] Includes sections:
  - **Evening Recap** header with timestamp
  - **Today's Memories Created**: List of memories created today
  - **Key Insights**: 3-5 important things learned/decided
  - **Tomorrow's Priorities**: Suggested focus areas based on memory content
- [ ] Uses OpenRouter Creative model for synthesis
- [ ] Configurable via env var: `EVENING_RECAP_TIME` (format: "HH:MM", default: "19:00")
- [ ] Creates daily note if doesn't exist

**Evening Recap Format**:
```markdown
## Evening Recap (19:00)

### Today's Memories Created
- [[API Architecture Decision]] - Chose REST over GraphQL (Semantic, 0.85)
- [[Team Standup Notes]] - Sprint progress discussion (Episodic, 0.6)
- [[Debugging Session]] - Fixed Nginx config issue (Procedural, 0.7)

### Key Insights
1. REST API chosen for better ecosystem compatibility
2. Nginx issue was rate limiting configuration
3. Sprint on track for Friday deadline

### Tomorrow's Priorities
Based on today's work:
- Complete API documentation (high salience)
- Follow up on performance testing (referenced in 3 memories)
- Schedule deployment review (FastTrack client mentioned)
```

---

### Story 3: Sunday Weekly Review

**As a** Brain OS user
**I want to** receive an automated weekly review every Sunday morning
**So that** I can review my week and plan the next one

**Acceptance Criteria**:
- [ ] New background task: `sunday_weekly_review_task`
- [ ] Runs every Sunday at configurable time (default: 07:00)
- [ ] Skips Saturday (Saturday nights don't get weekly reviews)
- [ ] Creates weekly note: `daily/YYYY-WXX-Review.md`
- [ ] Includes sections:
  - **Weekly Summary**: High-level overview of the week
  - **Key Themes**: 3-5 recurring topics
  - **Sector Analysis**: Cognitive balance check for the week
  - **Most Connected Entities**: Graph centrality insights
  - **Decisions Made**: Important decisions with rationale
  - **Next Week Focus**: Suggested priorities
- [ ] Uses OpenRouter Planning model for synthesis
- [ ] Configurable via env var: `WEEKLY_REVIEW_TIME` (format: "HH:MM", default: "07:00")
- [ ] Configurable day of week via env var: `WEEKLY_REVIEW_DAY` (default: "Sunday")

**Sunday Weekly Review Format**:
```markdown
# Weekly Review - Week XX (2026-01-12 to 2026-01-18)

## Weekly Summary
This week focused on Project X architecture decisions and FastTrack client work.
Made significant progress on API design and completed sprint goals.

## Key Themes
1. **API Architecture**: REST vs GraphQL decision, documentation standards
2. **Client Communication**: FastTrack requirements, N8N integration
3. **Infrastructure**: Nginx configuration, deployment pipeline

## Sector Analysis
This week's memory distribution:
- Episodic: 15 (35%)
- Semantic: 18 (42%)
- Procedural: 6 (14%)
- Emotional: 2 (5%)
- Reflective: 2 (5%)

✅ Good Semantic focus (decisions, knowledge)
⚠️ Low Emotional sector - consider work-life balance reflections

## Most Connected Entities
1. **Project X** - 12 linked memories
2. **PostgreSQL** - 8 linked memories
3. **FastTrack Client** - 6 linked memories

## Decisions Made
- REST API chosen for ecosystem compatibility
- PostgreSQL selected for ACID compliance
- N8N workflow approved for automation

## Next Week Focus
- Complete API documentation (referenced in 8 memories)
- Performance testing prep (mentioned in 5 memories)
- Client demo preparation (FastTrack)
```

---

### Story 4: Scheduled Background Task System

**As a** Brain OS system
**I want to** register and manage scheduled background tasks
**So that** updates run automatically at configured times

**Acceptance Criteria**:
- [ ] Enhanced `src/tasks/background.py` with cron-style scheduling
- [ ] Function: `register_scheduled_task(name: str, schedule: str, handler: callable)`
- [ ] Schedule format: Cron syntax ("0 7 * * *" = daily at 7 AM)
- [ ] Timezone support: Uses system timezone
- [ ] Task persistence: Last run timestamp tracked
- [ ] Overlap prevention: Skip if previous run still active
- [ ] Error handling: Failed tasks logged but don't block future runs
- [ ] Health check: `get_scheduled_tasks_status()` returns all task status

**Technical Implementation**:
```python
# src/tasks/background.py (enhanced)
from croniter import croniter
from datetime import datetime

class ScheduledTask:
    def __init__(self, name: str, schedule: str, handler: callable):
        self.name = name
        self.schedule = schedule  # Cron format
        self.handler = handler
        self.last_run = None
        self.is_running = False

    def should_run(self) -> bool:
        """Check if task should run now based on cron schedule."""
        if self.is_running:
            return False  # Skip if still running

        cron = croniter(self.schedule, datetime.now())
        next_run = cron.get_next(datetime)

        if self.last_run is None:
            return True

        # Should run if next scheduled time has passed
        return datetime.now() >= next_run

# Register tasks
def register_recurring_updates():
    """Register all scheduled update tasks."""
    register_scheduled_task(
        name="morning_briefing",
        schedule=os.getenv("MORNING_BRIEFING_CRON", "0 7 * * *"),  # 7 AM daily
        handler=run_morning_briefing
    )

    register_scheduled_task(
        name="evening_recap",
        schedule=os.getenv("EVENING_RECAP_CRON", "0 19 * * *"),  # 7 PM daily
        handler=run_evening_recap
    )

    register_scheduled_task(
        name="weekly_review",
        schedule=os.getenv("WEEKLY_REVIEW_CRON", "0 7 * * 0"),  # 7 AM Sunday
        handler=run_weekly_review
    )
```

---

### Story 5: Update Content Synthesis

**As a** Brain OS system
**I want to** generate appropriate content for each update type
**So that** updates are relevant and actionable

**Acceptance Criteria**:
- [ ] New flow: `morning_briefing_flow` (PocketFlow)
- [ ] New flow: `evening_recap_flow` (PocketFlow)
- [ ] New flow: `weekly_review_flow` (PocketFlow)
- [ ] Each flow:
  - Queries Neo4j for relevant memories
  - Analyzes sector distribution
  - Synthesizes insights using OpenRouter
  - Formats output for Obsidian markdown
- [ ] Context-aware synthesis:
  - Morning: Forward-looking, focus on today
  - Evening: Reflective, summary of accomplishments
  - Weekly: Strategic, pattern analysis
- [ ] Progress logging at each synthesis step

**Technical Implementation**:
```python
# src/flows/recurring_updates.py
from pocketflow import AsyncNode, AsyncFlow
from src.utils.llm import get_openrouter_client, get_openrouter_model

class MorningBriefingNode(AsyncNode):
    async def exec_async(self, inputs):
        # Get yesterday's memories
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        memories = await get_memories_by_date(yesterday)

        # Get instinctive memories for today's focus
        instinctive = await get_instinctive_memories(limit=5)

        # Get active projects
        projects = await get_active_projects()

        # Synthesize briefing
        client = await get_openrouter_client()
        model = get_openrouter_model("creative")

        response = await client.chat.completions.create(
            model=model,
            messages=[{
                "role": "system",
                "content": "Generate morning briefing from memory data."
            }, {
                "role": "user",
                "content": format_briefing_context(memories, instinctive, projects)
            }],
            temperature=0.7,
            max_tokens=1000
        )

        return {
            "content": response.choices[0].message.content,
            "type": "morning_briefing",
            "timestamp": datetime.now().isoformat()
        }

morning_briefing_flow = AsyncFlow(start=MorningBriefingNode())
```

---

### Story 6: Obsidian Note Creation

**As a** Brain OS system
**I want to** create and update Obsidian notes with update content
**So that** updates are visible and browsable in Obsidian

**Acceptance Criteria**:
- [ ] New utility: `create_or_update_daily_note(date: str)`
- [ ] New utility: `create_weekly_review_note(week: str)`
- [ ] Daily notes stored in: `daily/YYYY-MM-DD.md`
- [ ] Weekly notes stored in: `daily/YYYY-WXX-Review.md`
- [ ] Uses YuNaga224 Obsidian MCP server
- [ ] Graceful degradation if Obsidian unavailable
- [ ] Appends to existing notes (evening recap)
- [ ] Creates new notes if don't exist (morning briefing)

**Technical Implementation**:
```python
# src/utils/obsidian_notes.py
async def create_or_update_daily_note(content: str, section: str):
    """Create or append to daily note in Obsidian."""
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    today = datetime.now().strftime("%Y-%m-%d")
    note_path = f"{vault_path}/daily/{today}.md"

    # Check if note exists
    if os.path.exists(note_path):
        # Append section
        with open(note_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}\n")
    else:
        # Create new note with template
        await create_daily_note_from_template(today, content)

async def create_weekly_review_note(week: str, content: str):
    """Create weekly review note in Obsidian."""
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    note_path = f"{vault_path}/daily/{week}-Review.md"

    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(content)
```

---

### Story 7: Configuration & Environment Variables

**As a** developer
**I want to** configure all scheduled times via environment variables
**So that** users can customize update schedules

**Acceptance Criteria**:
- [ ] Environment variables documented in `.env.example`
- [ ] Validation of time format (HH:MM)
- [ ] Validation of day format (Monday, Tuesday, etc.)
- [ ] Default values provided for all variables
- [ ] CLI restart required for schedule changes

**Environment Variables**:
```env
# Scheduled Recurring Updates (Phase 3)

# Morning Briefing
MORNING_BRIEFING_ENABLED=true
MORNING_BRIEFING_TIME=07:00
MORNING_BRIEFING_CRON=0 7 * * *

# Evening Recap
EVENING_RECAP_ENABLED=true
EVENING_RECAP_TIME=19:00
EVENING_RECAP_CRON=0 19 * * *

# Weekly Review
WEEKLY_REVIEW_ENABLED=true
WEEKLY_REVIEW_DAY=Sunday
WEEKLY_REVIEW_TIME=07:00
WEEKLY_REVIEW_CRON=0 7 * * 0

# Obsidian Vault
OBSIDIAN_VAULT_PATH=/home/user/brain-os-vault
```

---

## Technical Requirements

### Dependencies

**Python (Brain OS)**:
- `croniter` - Cron schedule parsing
- Existing: `groq`, `openai` (for OpenRouter)
- Existing: `fastmcp` (for background tasks)

### File Changes

**New Files**:
- `src/flows/recurring_updates.py` - Morning/evening/weekly flows
- `src/utils/obsidian_notes.py` - Obsidian note management
- `src/tasks/scheduled.py` - Scheduled task system
- `templates/daily-note-template.md` - Daily note template
- `templates/weekly-review-template.md` - Weekly review template

**Modified Files**:
- `src/tasks/background.py` - Add cron scheduling
- `src/tools/memory/__init__.py` - Register update tools
- `.env.example` - Add scheduled update variables
- `brainos_server.py` - Register background tasks on startup

---

## Testing Plan

### Unit Tests

1. **Test Schedule Parsing**:
   - Valid cron formats → parsed correctly
   - Invalid formats → validation error
   - Timezone handling → correct conversion

2. **Test Content Synthesis**:
   - Memory data → appropriate briefing/recap/review
   - Empty memory set → helpful message
   - Large memory set → summarizes top results

### Integration Tests

1. **Test Morning Briefing**:
   - Schedule triggers at configured time
   - Note created in Obsidian
   - Content includes all sections
   - No duplicate notes if re-run

2. **Test Evening Recap**:
   - Appends to existing daily note
   - Creates note if doesn't exist
   - Content reflects today's memories

3. **Test Weekly Review**:
   - Runs on Sunday (not Saturday)
   - Creates weekly note with correct format
   - Includes week's data analysis

---

## Success Metrics

**Phase 3 Complete When**:
- ✅ Morning briefing runs at scheduled time
- ✅ Evening recap runs at scheduled time
- ✅ Sunday weekly review runs (skips Saturday)
- ✅ All updates appear in Obsidian
- ✅ Content is relevant and actionable
- ✅ System handles Obsidian downtime gracefully
- ✅ Times configurable via environment variables

**User Acceptance**:
- ✅ User wakes up to morning briefing in Obsidian
- ✅ User ends day with evening recap
- ✅ User reviews week on Sunday morning
- ✅ User confirms "This is exactly what I needed"

---

## Estimated Effort

| Story | Complexity | Effort |
|-------|------------|--------|
| Story 1: Morning Briefing | Medium | 4 hours |
| Story 2: Evening Recap | Medium | 3 hours |
| Story 3: Sunday Weekly Review | Medium | 4 hours |
| Story 4: Scheduled Task System | High | 5 hours |
| Story 5: Content Synthesis | Medium | 4 hours |
| Story 6: Obsidian Notes | Low | 2 hours |
| Story 7: Configuration | Low | 1 hour |

**Total Estimated Effort**: 23 hours

**Timeline**: 2-3 days of focused development

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Scheduled Update System                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  07:00 (Daily)        19:00 (Daily)        Sunday 07:00     │
│      │                    │                     │            │
│      ▼                    ▼                     ▼            │
│  Morning           Evening              Sunday Weekly        │
│  Briefing          Recap                Review               │
│      │                    │                     │            │
│      └────────────────────┴─────────────────────┘            │
│                           │                                  │
│                           ▼                                  │
│                  Query Neo4j Memories                       │
│                           │                                  │
│                           ▼                                  │
│              Synthesize (OpenRouter)                        │
│                           │                                  │
│                           ▼                                  │
│              Create/Update Obsidian Note                    │
│                           │                                  │
│                           ▼                                  │
│                   Log Success/Error                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps After Phase 3 Approval

1. User reviews Phase 3 user stories
2. User approves Phase 3 scope
3. I implement after Phase 2 completion
4. User tests with scheduled updates over 1 week
5. User approves Phase 3 completion
6. Brain OS + Obsidian integration COMPLETE! 🎉

---

**Phase 3 Status**: ⏳ Awaiting User Approval (after Phase 2)
**Dependencies**: Phase 1 and Phase 2 must be completed first
**Next Action**: User reviews Phase 3 user stories
