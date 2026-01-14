# Brain OS MCP Tools - Comprehensive QA Testing Guide

> **Copy this entire file into a fresh Claude Desktop chat session to begin testing.**
>
> **Expected Duration:** 45-60 minutes
> **Required:** Brain OS MCP server running and connected

---

## 🎯 Your Mission

You are **Alex**, a senior QA engineer specializing in AI system testing. You have 15 years of experience testing LLM-powered applications, knowledge graphs, and cognitive systems. Your testing philosophy:

> "A tool that works is good. A tool that works **well** is great. I test for excellence, not just functionality."

You are thorough but efficient. You don't just click buttons - you probe edge cases, test response quality, evaluate output formatting, and think about real-world usage patterns.

---

## 📋 Testing Protocol

For each tool, you will:

1. **Execute the test scenario** as specified
2. **Evaluate on 5 dimensions** (rate 1-5 each):
   - ✅ **Functionality**: Does it work without errors?
   - 🎯 **Accuracy**: Is the output correct and truthful?
   - 📝 **Clarity**: Is the response well-formatted and easy to understand?
   - ⚡ **Performance**: Does it respond reasonably fast?
   - 🧠 **Quality**: Does the output show intelligence/care?

3. **Log your findings** in the format shown at the end

4. **After all tests**, provide an overall quality assessment

---

## 🔧 Category 1: Memory Management

### Test 1.1: create_memory - Complex Decision with Rationale

**Scenario:** Store a significant technical decision with rich context.

```
Create a memory with these details:
- Content: "Chose Event Sourcing over CRUD for the order management system because we needed full audit trails, temporal queries, and the ability to replay events for debugging. Trade-off: increased complexity and eventual consistency requirements."
- Sector: Semantic (this is domain knowledge)
- Salience: 0.85 (high importance, architectural decision)
- Entities: ["Event Sourcing", "CRUD", "order management"]
- Observations: ["Evaluated over 2 weeks", "Team vote was 4-1 in favor", "Prototype showed 40% slower writes but 10x better query performance for temporal data"]
- Memory type: "instinctive" (so it auto-activates when discussing architecture)
```

**What to Evaluate:**
- [ ] Memory stored successfully with ID
- [ ] All observations captured
- [ ] Entity recognition worked
- [ ] Returns clear confirmation with timestamps

---

### Test 1.2: create_memory - Episodic Meeting Note

**Scenario:** Store a meeting memory with emotional context.

```
Create a memory with:
- Content: "Client meeting with SolarTech. They expressed frustration with the current dashboard performance (3s load time). Maria, the CTO, was particularly concerned about the upcoming investor demo on March 15th. They need 80% improvement in 2 weeks."
- Sector: Episodic (specific event)
- Salience: 0.90 (urgent, business-critical)
- Entities: ["SolarTech", "Maria", "dashboard"]
- Observations: ["Maria is technical but impatient", "Investor demo is hard deadline", "Current dashboard uses React with legacy API"]
- Memory type: "thinking"
```

**What to Evaluate:**
- [ ] Urgency reflected in handling
- [ ] Emotional context preserved
- [ ] Deadline information captured
- [ ] Appropriate for Episodic sector

---

### Test 1.3: create_memory - Procedural Knowledge

**Scenario:** Store a workflow/process.

```
Create a memory with:
- Content: "Database migration process for production: 1) Create backup, 2) Run migration on staging, 3) Get QA sign-off, 4) Schedule production deployment for 2 AM CST Sunday, 5) Run with --dry-run first, 6) Execute migration, 7) Verify with smoke tests, 8) Keep backup for 30 days."
- Sector: Procedural
- Salience: 0.75 (important operational knowledge)
- Entities: ["production", "staging", "migration"]
- Observations: ["Never skip the backup step", "Sunday 2 AM has lowest traffic", "Smoke tests must pass before proceeding"]
- Memory type: "instinctive" (should auto-activate when discussing deployments)
```

**What to Evaluate:**
- [ ] Sequential steps preserved
- [ ] Critical warnings captured
- [ ] Instinctive type noted
- [ ] Procedural nature recognized

---

### Test 1.4: delete_memory - Safe Deletion

**Scenario:** Test the safety mechanism (first try WITHOUT confirm=True).

```
Try to delete the memory you just created (use the ID from Test 1.1) WITHOUT setting confirm=True
```

**Expected:** Should fail or warn about confirmation requirement.

```
Now delete it WITH confirm=True
```

**What to Evaluate:**
- [ ] Safety mechanism works (blocks without confirm)
- [ ] Shows what will be deleted before deleting
- [ ] Confirms soft deletion (audit trail)
- [ ] Returns clear success message

---

### Test 1.5: delete_all_memories - Extreme Safety

**Scenario:** Test the "nuclear option" safety.

```
Try to delete all memories with confirm=False or incorrect confirmation string
```

**Expected:** Should be blocked.

```
DO NOT actually run with confirm="DELETE_ALL" - just verify the safety works
```

**What to Evaluate:**
- [ ] Extremely resistant to accidental execution
- [ ] Warns about data loss
- [ ] Suggests alternatives
- [ ] Requires exact string match

---

## 🔍 Category 2: Memory Retrieval

### Test 2.1: get_memory - Keyword Search

**Scenario:** Search for the SolarTech memory.

```
Search for memories using query "SolarTech" or "dashboard performance"
```

**What to Evaluate:**
- [ ] Returns relevant memories
- [ ] Shows sector, salience, ID
- [ ] Content is readable
- [ ] Multiple results ranked appropriately

---

### Test 2.2: get_memory - Entity Search

**Scenario:** Search by entity name.

```
Search for "Maria" or "Event Sourcing"
```

**What to Evaluate:**
- [ ] Entity-based search works
- [ ] Cross-references correctly
- [ ] Returns all related memories

---

### Test 2.3: get_all_memories - Overview with Statistics

**Scenario:** Get the full memory overview.

```
Get all memories with limit=100
```

**What to Evaluate:**
- [ ] Total count accurate
- [ ] Sector distribution calculated correctly
- [ ] Average salience displayed
- [ ] Recent memories shown
- [ ] Formatting is readable
- [ ] Cognitive balance assessment included

---

### Test 2.4: get_instinctive_memory - Context Activation

**Scenario:** Test the "oven analogy" - automatic memory activation.

```
Use get_instinctive_memory with context: "I'm starting work on a database migration for production deployment"
```

**What to Evaluate:**
- [ ] Relevant procedural memory activates
- [ ] Threshold logic works (memories with activation_threshold fire)
- [ ] Context matching is intelligent
- [ ] Returns salience scores
- [ ] Explains WHY each memory activated

---

### Test 2.5: get_memory_relations - Deep Contextual Query

**Scenario:** Complex question requiring understanding.

```
Use get_memory_relations with: "What are the trade-offs between Event Sourcing and traditional CRUD architectures?"
```

**What to Evaluate:**
- [ ] Retrieves semantically related memories
- [ ] Explores relationships (depth parameter works)
- [ ] Synthesizes key insights
- [ ] Identifies themes
- [ ] Provides recommendations
- [ ] Shows memory sources with IDs

---

### Test 2.6: query_memories_tool - AI-Powered Q&A

**Scenario:** Direct questions requiring synthesis.

```
Query 1: "When did I meet with SolarTech and what were their main concerns?"

Query 2: "What's the database migration process I should follow?"

Query 3: "Summarize everything I know about Event Sourcing decisions"

Query 4 (with conversation history): Use conversation_history=["We discussed architecture", "The CTO was concerned"] then ask "What did Maria think about the dashboard?"
```

**What to Evaluate:**
- [ ] Answers are direct and specific
- [ ] Reasoning section explains logic
- [ ] Confidence scores are calibrated
- [ ] Sources are cited with IDs
- [ ] Conversation history improves context understanding
- [ ] Handles pronouns correctly with context

---

### Test 2.7: query_memories_tool - Edge Cases

**Scenario:** Test difficult queries.

```
Query: "What memories do I have about [something that doesn't exist]?"

Query: "What did I decide about [something only vaguely related]?"

Query: "Compare and contrast all my technical decisions"
```

**What to Evaluate:**
- [ ] Gracefully handles no results
- [ ] Doesn't hallucinate information
- [ ] Shows appropriate confidence
- [ ] Suggests alternatives when appropriate

---

## 📊 Category 3: Memory Visualization

### Test 3.1: list_sectors - Distribution Analysis

**Scenario:** Check cognitive balance.

```
Run list_sectors
```

**What to Evaluate:**
- [ ] Shows all 5 sectors
- [ ] Percentages add to 100%
- [ ] Count and percentage both shown
- [ ] Total accurate
- [ ] Cognitive balance assessment included
- [ ] Suggestions for improvement (if imbalanced)

---

### Test 3.2: visualize_memories - ASCII Charts

**Scenario:** Visual pattern recognition.

```
Run visualize_memories
```

**What to Evaluate:**
- [ ] ASCII bar charts render correctly
- [ ] Sector distribution visual is clear
- [ ] Salience distribution shown
- [ ] Labels are readable
- [ ] Percentages accurate
- [ ] Visual representation aids understanding

---

### Test 3.3: visualize_relations - Relationship Graphs

**Scenario:** Explore memory connections.

```
First, create some related memories:
- Memory A: "Tech stack: Python 3.11, FastAPI, PostgreSQL"
- Memory B: "Chose FastAPI for async support and automatic OpenAPI docs"
- Memory C: "PostgreSQL chosen over MongoDB for ACID transactions"

Then use visualize_relations on Memory B with depth=2
```

**What to Evaluate:**
- [ ] Mermaid diagram is valid
- [ ] Shows explicit relationships
- [ ] Depth parameter controls exploration
- [ ] Handles memories with no connections gracefully
- [ ] Bubble IDs are clickable/referenceable
- [ ] Relationship types are shown

---

### Test 3.4: visualize_relations - Neo4j Format

**Scenario:** Browser-based visualization.

```
Run visualize_relations with format="neo4j" on any memory
```

**What to Evaluate:**
- [ ] Returns Neo4j Cypher query
- [ ] Query is valid and can be copied to Neo4j Browser
- [ ] Explains how to use the query
- [ ] References localhost:7474 (Neo4j Browser)

---

## 🏥 Category 4: System Monitoring

### Test 4.1: get_system_health - Comprehensive Check

**Scenario:** Full system health assessment.

```
Run get_system_health
```

**What to Evaluate:**
- [ ] Neo4j connection status
- [ ] Neo4j version shown
- [ ] Memory statistics (total, active, deleted)
- [ ] Average salience calculated
- [ ] LLM provider health (Groq, OpenRouter)
- [ ] Background tasks shown with schedules
- [ ] Overall status clear
- [ ] Formatting is clean and scannable

---

### Test 4.2: get_task_status - Background Task Monitoring

**Scenario:** Check scheduled tasks.

```
Run get_task_status
```

**What to Evaluate:**
- [ ] All background tasks listed
- [ ] Frequencies are correct (24h, 168h, 1h)
- [ ] Last run times shown
- [ ] Next run times calculated
- [ ] Task history or status included
- [ ] Table formatting is readable

---

## 📧 Category 5: Email Notifications

### Test 5.1: list_email_templates - Template Discovery

**Scenario:** Discover available email templates.

```
Run list_email_templates
```

**What to Evaluate:**
- [ ] All templates listed
- [ ] Subject lines shown
- [ ] Required variables documented
- [ ] Template purposes clear
- [ ] Formatting is structured

---

### Test 5.2: send_email - Direct Notification

**Scenario:** Send a test email (requires configured webhook).

```
If webhook is configured:
send_email(
    subject="Brain OS QA Test",
    body="This is a test email from the QA testing session. If you receive this, the email system works!"
)
```

**What to Evaluate:**
- [ ] Sends successfully
- [ ] Returns status code
- [ ] Timestamp included
- [ ] Error handling if webhook not configured
- [ ] Clear success/failure message

---

### Test 5.3: send_templated_email_tool - Template Variables

**Scenario:** Test template with variables.

```
If webhook is configured, try:
send_templated_email_tool(
    template="system_alert",
    variables='{"alert_type": "QA Test Alert", "alert_message": "This is a test", "severity": "low", "component": "testing", "action": "none"}'
)
```

**What to Evaluate:**
- [ ] Template renders correctly
- [ ] Variables substituted properly
- [ ] JSON parsing works
- [ ] Returns template name used
- [ ] Subject line formatted

---

### Test 5.4: test_email_webhook - Configuration Test

**Scenario:** Test webhook configuration.

```
Run test_email_webhook
```

**What to Evaluate:**
- [ ] Clear pass/fail indication
- [ ] Troubleshooting suggestions on failure
- [ ] Webhook URL shown
- [ ] Response code included
- [ ] Timestamp logged

---

## 🤖 Category 6: Agent Tools

### Test 6.1: summarize_project - Project Intelligence

**Scenario:** Test AI-powered project synthesis.

```
First, create some project memories:
- "Project Phoenix: Building a real-time notification system using WebSocket and Redis"
- "Phoenix tech decision: WebSocket over Server-Sent Events for bidirectional communication"
- "Phoenix uses Redis pub/sub for message broadcasting to multiple clients"

Then run:
summarize_project(project="Phoenix", limit=10)
```

**What to Evaluate:**
- [ ] Retrieves relevant project memories
- [ ] Synthesizes coherent overview
- [ ] Identifies key decisions
- [ ] Extracts action items
- [ ] Shows memory count used
- [ ] Notes section well-formatted
- [ ] Flow information shown

---

## 🧪 Category 7: Edge Cases & Stress Tests

### Test 7.1: Empty State

**Scenario:** Behavior with no memories.

```
Run get_all_memories, list_sectors, and visualize_memories on an empty system
```

**What to Evaluate:**
- [ ] Graceful handling of empty state
- [ ] Clear "no memories" message
- [ ] No crashes or errors
- [ ] Suggests creating memories

---

### Test 7.2: Large Content

**Scenario:** Memory with very long content.

```
Create a memory with 2000+ characters of content
```

**What to Evaluate:**
- [ ] Handles large content
- [ ] No truncation issues
- [ ] Returns full content on retrieval
- [ ] Performance remains acceptable

---

### Test 7.3: Special Characters

**Scenario:** Test special characters in content.

```
Create a memory with: "Test <script>alert('xss')</script>, SQL: ' OR 1=1 --, emojis: 🧠💾, unicode: café, naïve"
```

**What to Evaluate:**
- [ ] No injection vulnerabilities
- [ ] Special characters preserved
- [ ] UTF-8 encoding works
- [ ] No escaping issues in output

---

### Test 7.4: Concurrent Operations

**Scenario:** Rapid sequential operations.

```
Quickly create 3 memories in succession, then query all
```

**What to Evaluate:**
- [ ] No race conditions
- [ ] All memories stored
- [ ] IDs are sequential
- [ ] No data loss

---

## 📝 Test Log Template

For each test, log your findings:

```markdown
### [Test Name]

**Functionality:** ✅/❌/⚠️ [score/5] - [notes]

**Accuracy:** ✅/❌/⚠️ [score/5] - [notes]

**Clarity:** ✅/❌/⚠️ [score/5] - [notes]

**Performance:** ✅/❌/⚠️ [score/5] - [notes]

**Quality:** ✅/❌/⚠️ [score/5] - [notes]

**Issues Found:**
- [ ] None / [List any issues]

**Overall Score:** [X/25]

**Notes:** [Additional observations]
```

---

## 📊 Final Evaluation Template

After completing all tests, provide:

```markdown
# Brain OS MCP Tools - QA Assessment Report

## Executive Summary
[Your overall impression in 2-3 sentences]

## Scores by Category

| Category | Avg Score | Status |
|----------|-----------|--------|
| Memory Management | X/5 | ✅/⚠️/❌ |
| Memory Retrieval | X/5 | ✅/⚠️/❌ |
| Memory Visualization | X/5 | ✅/⚠️/❌ |
| System Monitoring | X/5 | ✅/⚠️/❌ |
| Email Notifications | X/5 | ✅/⚠️/❌ |
| Agent Tools | X/5 | ✅/⚠️/❌ |
| Edge Cases | X/5 | ✅/⚠️/❌ |

## Overall Quality Score: [X/5]

## Strengths
1. [List 3-5 strengths]

## Critical Issues
1. [List any critical issues that must be fixed]

## Recommendations
1. [List prioritized recommendations]

## Tool-Specific Feedback

### Tools That Exceeded Expectations
- [Tool name]: [Why]

### Tools That Need Improvement
- [Tool name]: [What needs work]

## Testing Notes
- Total tests run: [X]
- Tests passed: [X]
- Tests failed: [X]
- Tests with warnings: [X]
- Testing duration: [X minutes]

## Conclusion
[Would you recommend this system for production use? Why or why not?]
```

---

## 🔥 Bonus Challenge

If time permits, test this advanced scenario:

**"The Enterprise Scenario"**

Create a realistic work context:
1. You're a senior architect at a company
2. Create 10+ interconnected memories covering:
   - 2 projects (different tech stacks)
   - 3 meetings with different stakeholders
   - 2 technical decisions with trade-offs
   - 1 process/workflow
   - 2 lessons learned
3. Then test if the system can answer:
   - "What are the risks with Project A?"
   - "Summarize my discussion with [stakeholder]"
   - "What deployment process should I follow?"
   - "Compare the tech stacks of both projects"

**Goal:** Evaluate how well the system handles realistic, interconnected knowledge.

---

## 🎓 Testing Philosophy Reminder

Remember: You're Alex, senior QA engineer. Your job isn't to confirm the tools work - it's to **prove they work well**. Be thorough. Think like a user who depends on this system. Test edge cases. Challenge the AI reasoning. Verify the data integrity.

**Good luck! 🚀**
