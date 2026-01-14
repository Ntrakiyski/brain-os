# Phase 4: Obsidian Integration - Summary

**Status**: Design Complete - Awaiting User Approval
**Date**: 2026-01-13

---

## Quick Overview

This document summarizes the 3-phase approach to integrating Obsidian with Brain OS.

| Phase | Goal | User Stories | Effort | Status |
|-------|------|--------------|--------|--------|
| **Phase 1** | Neo4j → Obsidian sync on memory creation | 8 stories | 13 hours | ⏳ Awaiting Approval |
| **Phase 2** | Bidirectional sync (cron every 15min) + bulk export | 8 stories | 22 hours | ⏳ Awaiting Approval |
| **Phase 3** | Scheduled recurring updates (morning/evening/weekly) | 7 stories | 23 hours | ⏳ Awaiting Approval |

**Total Effort**: ~58 hours (5-7 days of focused development)

---

## Phase 1: Basic Neo4j → Obsidian Sync

**Goal**: When I create a memory → File appears in Obsidian

### Key Features
- ✅ Connect to YuNaga224/obsidian-memory-mcp server
- ✅ `create_memory` tool creates entity in Obsidian vault
- ✅ File has YAML frontmatter + markdown body
- ✅ Works with local Obsidian (free version)
- ✅ Graceful degradation if Obsidian offline

### User Stories
1. Setup Obsidian MCP Server Locally
2. Add Obsidian MCP Client to Brain OS
3. Create Entity Name Generator Utility
4. Enhance `create_memory` to Sync to Obsidian
5. Create Obsidian Entity File Structure
6. Add Environment Variable for Obsidian MCP URL
7. Test End-to-End Memory Creation
8. Handle Obsidian MCP Server Offline

### Success Criteria
- Create memory in Brain OS → Entity file appears in Obsidian
- Open Obsidian → See entity in graph view
- Search in Obsidian → Find entity by content
- Neo4j remains source of truth

**Timeline**: 1-2 days

**Full Document**: [phase1_user_stories.md](./phase1_user_stories.md)

---

## Phase 2: Bidirectional Sync + Bulk Export

**Goal**: Cron job syncs Obsidian → Neo4j every 15 minutes

### Key Features
- ✅ Background cron job (every 15 minutes)
- ✅ Detects changed files in Obsidian vault
- ✅ Updates Neo4j bubbles with Obsidian edits
- ✅ Conflict resolution (newest timestamp wins)
- ✅ Bulk export tool for existing memories
- ✅ Entity relationships in graph view
- ✅ Manual sync trigger

### User Stories
1. Parse Obsidian Entity Files
2. Detect Changed Files in Obsidian Vault
3. Update Neo4j Bubble from Obsidian Entity
4. Create Cron Job for Bidirectional Sync
5. Handle Sync Conflicts
6. Bulk Export Existing Memories to Obsidian
7. Create Entity Relationships in Obsidian
8. Add Manual Sync Trigger Tool

### Success Criteria
- Edit file in Obsidian → Neo4j updates in 15 minutes
- Bulk export 50+ memories → All appear in Obsidian
- Obsidian graph view shows entity relationships
- Conflicts resolved correctly (newest wins)

**Timeline**: 2-3 days

**Full Document**: [phase2_user_stories.md](./phase2_user_stories.md)

---

## Phase 3: Scheduled Recurring Updates

**Goal**: Automated daily and weekly updates sent to Obsidian at configurable times

### Key Features
- ✅ Morning Briefing (configurable time, default 7:00 AM)
- ✅ Evening Recap (configurable time, default 7:00 PM)
- ✅ Sunday Weekly Review (configurable time, default 7:00 AM, skips Saturday)
- ✅ Cron-style scheduling system
- ✅ All times configurable via environment variables
- ✅ Content synthesis using OpenRouter
- ✅ Graceful handling if Obsidian unavailable

### User Stories
1. Morning Briefing Update (yesterday's recap, today's focus, active projects)
2. Evening Recap Update (today's memories, key insights, tomorrow's priorities)
3. Sunday Weekly Review (weekly summary, key themes, sector analysis, decisions made)
4. Scheduled Background Task System (cron scheduling, overlap prevention)
5. Update Content Synthesis (context-aware generation for each update type)
6. Obsidian Note Creation (daily/weekly note management)
7. Configuration & Environment Variables (all times configurable)

### Success Criteria
- Morning briefing runs automatically at scheduled time
- Evening recap runs automatically at scheduled time
- Sunday weekly review runs (skips Saturday)
- All updates appear in Obsidian with relevant content
- Times configurable via environment variables

**Timeline**: 2-3 days

**Full Document**: [phase3_user_stories.md](./phase3_user_stories.md)

---

## Architecture Decisions

### 1. Obsidian MCP Server: YuNaga224/obsidian-memory-mcp

**Why?**
- ✅ Entity-Observation-Relation model (perfect match for Brain OS)
- ✅ No plugins required (works with fresh Obsidian install)
- ✅ File-based (works without Obsidian running)
- ✅ Semantic relationships: `[[Manager of::Alice]]`

### 2. Data Distribution: Neo4j + Obsidian (Complementary)

**Neo4j ONLY** (Computational):
- Salience scoring & decay
- Activation thresholds
- Complex graph queries
- Soft deletion audit trail

**BOTH** (Synchronized):
- Content, entities, observations
- Sector, memory type, source, dates
- Salience (as metadata only)

**Obsidian ONLY** (Human Interface):
- Markdown formatting
- Visual graph view
- Daily notes structure
- Tags, Dataview queries

### 3. Sync Strategy

**Phase 1**: One-way (Neo4j → Obsidian)
**Phase 2**: Bidirectional (cron job every 15 minutes)
**Phase 3**: Enhanced workflows (voice memos, daily notes)

### 4. Conflict Resolution

**Strategy**: Newest timestamp wins
- Compare `last_accessed` (Neo4j) vs `updated` (Obsidian frontmatter)
- If Neo4j newer → skip Obsidian sync
- If Obsidian newer → update Neo4j
- Log conflicts to `logs/obsidian_sync_conflicts.log`

---

## File Structure in Obsidian Vault

```
brain-os-vault/
├── entities/                     # Main entity pages
│   ├── Project_X.md
│   ├── PostgreSQL_Decision.md
│   └── FastTrack_Client.md
├── daily/                        # Daily notes
│   ├── 2026-01-13.md
│   └── 2026-W02-Review.md
├── sectors/                      # Organized by cognitive sector
│   ├── Episodic/
│   ├── Semantic/
│   ├── Procedural/
│   ├── Emotional/
│   └── Reflective/
└── templates/                    # Templater templates
    ├── daily-note.md
    └── weekly-review.md
```

---

## Testing Strategy

### Phase 1 Testing
- Create 10 test memories via Brain OS
- Verify all appear in Obsidian vault
- Check graph view, search, file content
- Test offline mode (Obsidian MCP unavailable)

### Phase 2 Testing
- Edit 5 files in Obsidian
- Wait 15 minutes (or trigger manual sync)
- Verify Neo4j updated correctly
- Bulk export 50 memories, check Obsidian
- Test conflict resolution (edit both Neo4j and Obsidian)

### Phase 3 Testing
- Record 15-minute voice memo
- Run `process_voice_memo(file_path)`
- Verify 3-5 memories created
- Check daily note updated
- Explore graph view relationships
- Run weekly review, verify synthesis

---

## Dependencies

### Software
- **Node.js v18+**: For Obsidian MCP server
- **Obsidian Desktop** (free version): For viewing vault
- **Neo4j**: Already running
- **Brain OS**: Existing setup
- **Note**: Claude handles transcription via MCP (no additional API keys needed)

### Python Packages (New)
- `PyYAML` - Parse Obsidian YAML frontmatter (Phase 2)

### Environment Variables (New)
```env
# Obsidian Integration
OBSIDIAN_MCP_URL=http://localhost:8001/mcp
OBSIDIAN_VAULT_PATH=/home/user/brain-os-vault
OBSIDIAN_SYNC_INTERVAL_MINUTES=15
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **YuNaga224 server fails** | High | Fallback: Neo4j continues, queue for retry |
| **Obsidian file corruption** | Medium | Git-based version control recommended |
| **Sync conflicts** | Medium | Timestamp-based resolution + conflict log |
| **Large vaults (500+ entities)** | Medium | Obsidian handles 10k+ notes, should be fine |

---

## Success Metrics (All Phases Complete)

**Technical**:
- ✅ 100+ memories exported to Obsidian
- ✅ Bidirectional sync works (edit Obsidian → Neo4j updates)
- ✅ Scheduled updates run reliably (morning/evening/weekly)
- ✅ Graph view with 50+ entities + relationships
- ✅ Daily notes auto-created and updated
- ✅ Zero data loss (Neo4j ↔ Obsidian consistency)

**User Experience**:
- ✅ User creates memory → sees in Obsidian instantly
- ✅ User edits Obsidian → Neo4j syncs in 15 minutes
- ✅ User receives morning briefing → starts day with context
- ✅ User receives evening recap → ends day with summary
- ✅ User receives weekly review → plans next week
- ✅ User confirms: "This is exactly what I needed"

---

## What Happens After Phase 3?

**Potential Phase 4+ Features** (Future):
- Real-time sync (remove 15-minute delay)
- Mobile app integration
- Multi-user support (shared vault)
- AI-powered relationship inference
- Video processing (extract audio + transcribe)
- Speaker diarization (who said what in meetings)
- Integration with other MCP servers (Gmail, Calendar)

---

## Approval Process

### Step 1: Review Phase Documents (Now)
- Read [phase1_user_stories.md](./phase1_user_stories.md)
- Read [phase2_user_stories.md](./phase2_user_stories.md)
- Read [phase3_user_stories.md](./phase3_user_stories.md)

### Step 2: Approve or Request Changes
- Approve Phase 1 → I start implementation
- Request changes → I update user stories
- Questions → I clarify design decisions

### Step 3: Phase 1 Implementation
- I implement all 8 user stories
- You test locally with Obsidian
- You approve completion → Move to Phase 2

### Step 4: Phase 2 Implementation
- I implement bidirectional sync
- You test editing Obsidian files
- You approve completion → Move to Phase 3

### Step 5: Phase 3 Implementation
- I implement scheduled recurring updates
- You test with morning/evening/weekly updates for 1 week
- You approve completion → **DONE!** 🎉

---

## Questions for User

Before proceeding, please answer:

1. **Approve all 3 phases?** Or request changes?

2. **Phase 1 priority?** Should I start immediately?

3. **Obsidian vault location?** Where should I create `/home/user/brain-os-vault`?

4. **Cron interval?** 15 minutes OK, or prefer different frequency?

5. **Scheduled update times?** Morning 7am, Evening 7pm, Sunday 7am OK?

---

## Next Steps

**Awaiting User Decision**:
- [ ] User reviews 3 phase documents
- [ ] User approves Phase 1 (or requests changes)
- [ ] User confirms Obsidian vault location
- [ ] User confirms scheduled update times (Phase 3)
- [ ] I proceed with Phase 1 implementation

---

**Total Estimated Timeline**: 5-7 days for all 3 phases
**Current Status**: ⏳ Design Complete - Awaiting Approval
**Next Action**: User reviews and approves Phase 1

---

## Contact

If you have questions about any phase:
- Read full phase document (linked above)
- Ask for clarification on specific user stories
- Request changes to scope or approach
- Suggest additional features

**I'm ready to start implementation as soon as you approve Phase 1!** 🚀
