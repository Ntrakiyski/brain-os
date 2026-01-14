# Brain OS Testing Plan Template

This document provides a standardized testing template to be used after each phase completion.

**Purpose:** Ensure consistent testing coverage and quality assurance across all development phases.

**Last Updated:** 2026-01-09

---

## Phase Testing Checklist

Use this checklist after completing each phase to ensure comprehensive testing.

### 1. Environment Setup

- [ ] Neo4j container is running (`docker ps` shows neo4j container)
- [ ] Neo4j Browser accessible at http://localhost:7474
- [ ] MCP server container is built and running
- [ ] Environment variables are properly configured
- [ ] Test script is executable (`uv run python test_*.py`)

### 2. Unit Tests

- [ ] All new tools have unit tests in `test_*.py`
- [ ] Test coverage > 80% for new code
- [ ] Edge cases are tested (empty inputs, invalid data, etc.)
- [ ] Error handling is verified

### 3. Integration Tests

- [ ] Tool-to-database integration works (Neo4j operations)
- [ ] Tool-to-LLM integration works (Groq, OpenRouter calls)
- [ ] Multi-step workflows complete successfully
- [ ] Async operations complete without hanging

### 4. Tool-Specific Tests

For each new tool, verify:

#### Basic Functionality
- [ ] Tool accepts all defined parameters
- [ ] Tool handles missing optional parameters correctly
- [ ] Tool validates input types and ranges
- [ ] Tool returns expected output format

#### Error Handling
- [ ] Invalid inputs return helpful error messages
- [ ] Missing dependencies are caught and reported
- [ ] Database errors are handled gracefully
- [ ] LLM API failures have fallback behavior

#### Performance
- [ ] Tool completes within expected time limits
- [ ] No memory leaks in async operations
- [ ] Database queries are optimized
- [ ] LLM calls use appropriate models

### 5. End-to-End Tests

- [ ] Complete user workflows work end-to-end
- [ ] Multiple tools can be chained successfully
- [ ] Data persists correctly across operations
- [ ] Visualization outputs are valid

### 6. Deployment Tests

- [ ] Docker image builds successfully
- [ ] Container starts without errors
- [ ] Health check endpoint responds
- [ ] MCP endpoint is accessible
- [ ] Environment variables are loaded correctly

### 7. Documentation

- [ ] All new tools documented in `docs/TOOLS_REFERENCE.md`
- [ ] API changes documented in `docs/project/phaseX/api-changes.md`
- [ ] User stories updated in `docs/project/phaseX/user-stories.md`
- [ ] CLAUDE.md updated with phase status
- [ ] Code comments are clear and accurate

### 8. Regression Tests

- [ ] Previous phase tools still work
- [ ] No breaking changes to existing APIs
- [ ] Database schema is backward compatible
- [ ] Configuration changes don't break existing setups

---

## Testing Commands Reference

### Local Testing

```bash
# Start services
docker compose -f docker-compose-test.yml up --build -d

# Run comprehensive test suite
uv run python test_all_tools.py

# Run phase-specific tests
uv run python test_phase3.py

# Check container status
docker ps -a --filter "name=brainos"

# View container logs
docker logs brainos-server-test --tail 50

# Cleanup
docker compose -f docker-compose-test.yml down
docker stop neo4j-test && docker rm neo4j-test
```

### Individual Tool Testing

```bash
# Test single tool via Python REPL
uv run python
>>> from fastmcp import Client
>>> async with Client("http://127.0.0.1:9131/mcp") as client:
...     result = await client.call_tool("tool_name", {"param": "value"})
...     print(result.data)
```

### Database Verification

```bash
# Connect to Neo4j Browser
# URL: http://localhost:7474
# Credentials: neo4j / brainos_password_123

# Verify schema
MATCH (b:Bubble) RETURN count(b) as total_bubbles

# Verify relationships
MATCH ()-[r:LINKED]->() RETURN count(r) as total_relations

# Check Phase 3 fields
MATCH (b:Bubble) WHERE b.memory_type IS NOT NULL RETURN b.memory_type, count(*)
```

---

## Test Result Template

After completing phase testing, create a summary using this format:

```markdown
# Phase X Test Results

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Phase:** [Phase Name/Number]

## Summary

- **Total Tools Tested:** X
- **Passed:** Y
- **Failed:** Z
- **Success Rate:** (Y/X * 100)%

## Test Coverage

### New Tools (Phase X)
| Tool | Status | Notes |
|------|--------|-------|
| tool_1 | PASS | - |
| tool_2 | PASS | - |
| tool_3 | FAIL | Issue description |

### Regression Tests (Previous Phases)
| Tool | Status | Notes |
|------|--------|-------|
| tool_a | PASS | - |
| tool_b | PASS | - |

## Issues Found

### Critical
- [Issue description]
- **Impact:** [What breaks]
- **Fix:** [How to fix]

### Minor
- [Issue description]
- **Impact:** [What breaks]
- **Fix:** [How to fix]

## Performance Metrics

| Tool | Expected Time | Actual Time | Status |
|------|---------------|-------------|--------|
| tool_1 | ~100ms | 95ms | OK |
| tool_2 | ~2-5s | 4.2s | OK |

## Next Steps

- [ ] Fix critical issues
- [ ] Address minor issues
- [ ] Update documentation
- [ ] Mark phase as complete in CLAUDE.md
```

---

## Phase-Specific Testing Guidelines

### Phase 1: Core Infrastructure
**Focus:** Basic CRUD operations and MCP server functionality

**Critical Tests:**
- Memory creation and retrieval
- Neo4j connectivity
- MCP server startup and tool registration
- Docker container build and deployment

**Success Criteria:**
- All 5 core tools work (create_memory, get_memory, get_all_memories, list_sectors, visualize_memories)
- MCP server responds to health checks
- Data persists across container restarts

### Phase 2: Agent Architecture
**Focus:** Modular tools and LLM integration

**Critical Tests:**
- Tool modularization (separate files, proper imports)
- LLM client factory (Groq, OpenRouter)
- Agent tool (summarize_project)
- Configuration-driven behavior

**Success Criteria:**
- Tools organized by function in separate files
- LLM calls work with both Groq and OpenRouter
- Agent behavior changes via configuration only
- Server line count reduced by >50%

### Phase 3: Advanced Memory
**Focus:** Instinctive activation and contextual retrieval

**Critical Tests:**
- Instinctive memory activation (Oven Analogy)
- 3-agent contextual retrieval
- Entity-observation model
- Relationship visualization
- PocketFlow migration from BaseAgent

**Success Criteria:**
- Instinctive memories auto-activate based on context
- Contextual retrieval returns themed, relevant results
- Entity and observation fields persist correctly
- Mermaid diagrams generate successfully
- All 9 tools pass integration tests
- 100% test success rate

### Phase 4: [Future]
**Focus:** [To be determined]

**Critical Tests:**
- [TBD]

**Success Criteria:**
- [TBD]

---

## Common Testing Scenarios

### Scenario 1: Empty Database
**Setup:** Fresh Neo4j instance with no data

**Tests:**
- get_all_memories returns "No memories stored yet"
- get_memory returns "No memories found"
- visualize_memories shows zero counts

### Scenario 2: Large Dataset
**Setup:** 100+ memories across all sectors

**Tests:**
- get_all_memories handles limit parameter correctly
- Search performance remains acceptable
- Sector distribution calculates correctly
- No memory leaks in long-running operations

### Scenario 3: Concurrent Access
**Setup:** Multiple simultaneous MCP clients

**Tests:**
- No race conditions in memory creation
- Access counts increment correctly
- Async operations don't block each other
- Database connection pooling works

### Scenario 4: Invalid Inputs
**Setup:** Various invalid parameter combinations

**Tests:**
- Negative salience values rejected
- Invalid sector names rejected
- Empty content rejected
- Out-of-range limits handled
- Type mismatches caught by validation

### Scenario 5: LLM Failures
**Setup:** Mock LLM API failures

**Tests:**
- Groq failures have fallback behavior
- OpenRouter failures return helpful messages
- Timeout handling works
- Rate limiting doesn't crash the server

---

## Test Data Sets

### Minimal Test Data
```python
# Minimum data for basic functionality
memories = [
    {"content": "Test memory 1", "sector": "Semantic", "salience": 0.5},
    {"content": "Test memory 2", "sector": "Episodic", "salience": 0.7}
]
```

### Comprehensive Test Data
```python
# Full coverage across sectors and features
memories = [
    # Basic memories
    {"content": "API uses FastAPI", "sector": "Semantic", "salience": 0.8, "memory_type": "instinctive"},
    {"content": "Deployment uses Docker", "sector": "Procedural", "salience": 0.7, "memory_type": "instinctive"},
    {"content": "Team meeting on Monday", "sector": "Episodic", "salience": 0.5, "memory_type": "thinking"},

    # Entity-observation test
    {"content": "Project A decision: PostgreSQL over MongoDB", "sector": "Semantic", "salience": 0.9,
     "memory_type": "instinctive", "entities": ["Project A", "PostgreSQL", "MongoDB"],
     "observations": ["ACID compliance", "Transaction support"]},

    # All sectors
    {"content": "Feeling confident about progress", "sector": "Emotional", "salience": 0.6},
    {"content": "Learning that iteration improves quality", "sector": "Reflective", "salience": 0.7}
]
```

---

## Bug Reporting Template

When bugs are found during testing, report them using this format:

```markdown
## Bug Report

**Title:** [Brief bug description]

**Phase:** [X]
**Tool:** [tool_name]
**Severity:** [Critical/High/Medium/Low]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Error Messages
```
[Paste error messages here]
```

### Environment
- Python version: [3.14.x]
- Neo4j version: [5.25-community]
- Docker version: [x.x.x]
- Operating System: [Windows/Linux/macOS]

### Logs
```
[Paste relevant logs here]
```

### Workaround
[If applicable, how to work around the bug]

### Fix Status
- [ ] Identified
- [ ] Fix implemented
- [ ] Test created
- [ ] Deployed
```

---

## Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests pass (100% success rate)
- [ ] No critical bugs outstanding
- [ ] Documentation is complete and accurate
- [ ] Environment variables are documented
- [ ] Docker image builds without warnings
- [ ] Health check endpoint works
- [ ] Memory usage is within limits
- [ ] Response times are acceptable
- [ ] Error handling is comprehensive
- [ ] Logging is adequate for debugging
- [ ] Backup strategy is in place
- [ ] Rollback plan is documented

---

## Continuous Testing Strategy

### Automated Testing
- Run `test_all_tools.py` after every code change
- Run tests in CI/CD pipeline before merging
- Maintain >80% code coverage

### Manual Testing
- Perform end-to-end testing before releases
- Test on target deployment environment
- Verify documentation accuracy

### Regression Testing
- Re-test all previous phase features after each new phase
- Maintain backward compatibility
- Test data migrations between schema versions

---

## Testing Best Practices

1. **Test Early, Test Often**
   - Write tests alongside code
   - Run tests frequently during development
   - Fix bugs immediately when found

2. **Test Isolation**
   - Each test should be independent
   - Tests should not rely on execution order
   - Clean up test data after each run

3. **Meaningful Assertions**
   - Test behavior, not implementation
   - Use descriptive assertion messages
   - Cover edge cases and error conditions

4. **Performance Testing**
   - Measure and track tool execution times
   - Test with realistic data volumes
   - Profile slow operations

5. **Documentation Testing**
   - Verify code examples in documentation
   - Keep API docs in sync with implementation
   - Update usage examples for new features

---

## Appendix: Test Scripts Reference

### test_all_tools.py
Comprehensive test suite for all 9 tools across Phase 2 and Phase 3.

**Usage:**
```bash
uv run python test_all_tools.py
```

**Output:** Summary showing pass/fail for each tool with success rate.

### test_phase3.py
Phase 3 specific tests for instinctive memory and contextual retrieval.

**Usage:**
```bash
uv run python test_phase3.py
```

**Output:** Detailed test results for Phase 3 features only.

### test-local.bat
Windows batch script for local testing automation.

**Usage:**
```cmd
test-local.bat
```

**What it does:**
1. Starts Neo4j container
2. Builds and starts BrainOS container
3. Runs phase tests
4. Displays cleanup commands

---

**End of Testing Plan Template**
