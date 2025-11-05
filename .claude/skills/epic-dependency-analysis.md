---
name: epic-dependency-analysis
description: After completing an epic or when planning next work, analyze epics and stories to identify sequential dependencies and parallel work opportunities for optimal development flow
---

# Epic Dependency Analysis Skill

## When to Use This Skill

Use this skill in these scenarios:
1. **After completing an epic** - Understand what can be done next
2. **Before starting sprint planning** - Identify parallel work opportunities
3. **When asked "what should we work on next?"** - Provide dependency-aware recommendations
4. **When planning team allocation** - Identify stories that can be parallelized

## What This Skill Does

Analyzes epic and story files to produce a **dependency map** and **parallelization strategy** that helps optimize development workflow.

## Analysis Process

### Step 1: Read Epic and Story Files
- Read all epic files in `docs/prd/epic-*.md`
- Read all story files in `docs/stories/`
- Read `docs/sprint-status.yaml` for current status

### Step 2: Identify Dependencies

**Data Dependencies:**
- Does Story B require data structures from Story A?
- Does Epic 3 need data from Epic 1?

**Feature Dependencies:**
- Does Story B build on functionality from Story A?
- Does Epic 4 require features from Epic 2?

**Infrastructure Dependencies:**
- Does Story B need APIs/modules from Story A?
- Does Epic 6 need authentication from Epic 5?

**Testing Dependencies:**
- Does Story B need test data from Story A?
- Does Epic 7 need all other epics complete for evaluation?

### Step 3: Identify Parallel Opportunities

Stories/epics that can run in parallel have:
- No shared data structures
- Independent functionality
- Different code modules
- No infrastructure overlap

### Step 4: Create Dependency Graph

Output format:
```
EPIC X: [Name]
├─ Must complete first: [List]
├─ Can run parallel with: [List]
├─ Blocks: [List]
└─ Stories:
   ├─ Story X.Y: [dependencies]
   └─ Story X.Z: [can run parallel with X.Y if...]
```

## Output Template

```markdown
# Epic Dependency Analysis - [Date]

## Current Status
- Completed: Epic X, Epic Y (Stories: X.1, X.2, Y.1...)
- In Progress: Story Z.3
- Blocked: None

## Dependency Map

### Epic 1: [Name]
**Status:** [done/in-progress/backlog]
**Dependencies:** None (foundation epic)
**Blocks:** Epic 2, Epic 3
**Stories:**
- 1.1: ✅ Done
- 1.2: ✅ Done
- 1.3: ✅ Done
- 1.4: 🔄 Next (no dependencies within epic)

### Epic 2: [Name]
**Status:** [backlog]
**Dependencies:** Epic 1 stories 1.1, 1.2 (needs data schema and profiles)
**Blocks:** Epic 3, Epic 4
**Can run parallel with:** Epic 5 (after Epic 1 done)
**Stories:**
- 2.1: Ready to start (needs 1.2 data schema)
- 2.2-2.6: Can parallelize after 2.1 (independent signal detections)

### Epic 3: [Name]
**Status:** [backlog]
**Dependencies:** Epic 2 (needs behavioral signals)
**Blocks:** Epic 4
**Can run parallel with:** Epic 5, Epic 6 (partial)

## Parallelization Opportunities

### Current Sprint Options
1. **Single Developer:**
   - Next: Story 1.4 (continues Epic 1)
   - Then: Story 1.5 (same epic, builds on 1.4)

2. **Two Developers:**
   - Dev 1: Story 1.4 (transactions)
   - Dev 2: Story 5.1 (consent system - independent)

3. **Three+ Developers:**
   - Dev 1: Story 1.4
   - Dev 2: Story 5.1
   - Dev 3: Story 6.1 (authentication - independent)

### Critical Path
```
Epic 1 → Epic 2 → Epic 3 → Epic 4 → Epic 7
         ↓
         Epic 5 (can start after Epic 1)
         Epic 6 (can start anytime)
```

## Recommendations

### Immediate Next Steps
1. **Highest Priority:** Story 1.4 (unblocks rest of Epic 1)
2. **Parallel Work:** Story 5.1 (independent, unblocks Epic 5)
3. **Future Planning:** Review Epic 2 tech specs (will be needed soon)

### Risk Mitigation
- **Bottleneck:** Epic 2 → Epic 3 → Epic 4 are sequential
- **Mitigation:** Start Epic 5, Epic 6 in parallel to utilize team capacity
- **Testing:** Epic 7 should start incremental metrics during other epics

### Optimization Strategy
- Complete Epic 1 fully before starting Epic 2 (clean data foundation)
- Start Epic 5 after Epic 1 (provides guardrails for later epics)
- Epic 6 can start anytime (UI/operator features)
- Epic 7 should be incremental (add metrics per epic, not at end)

## Story-Level Dependencies Within Epics

### Epic 1 Stories
- 1.1 → 1.2 → 1.3 → 1.4 → 1.5 (sequential, each builds on previous)
- 1.6 can run parallel with 1.4/1.5 (validation pipeline independent)

### Epic 2 Stories
- 2.1 first (framework)
- 2.2, 2.3, 2.4, 2.5 can ALL run in parallel (independent signals)
- 2.6 last (aggregation needs all signals)

## Notes
- [Any special considerations]
- [Technical debt that affects dependencies]
- [External dependencies or blockers]
```

## Critical Requirements

1. **Be Accurate**: Read actual epic/story files, don't assume
2. **Be Specific**: Name exact stories and their dependencies
3. **Be Practical**: Focus on what can actually be parallelized
4. **Consider Resources**: Acknowledge team size constraints
5. **Identify Risks**: Call out sequential bottlenecks early

## Analysis Checklist

When running this skill, create TodoWrite todos for:
- [ ] Read sprint-status.yaml for current state
- [ ] Read all epic files to understand scope
- [ ] Read completed story files for context
- [ ] Read next 3-5 story files to understand upcoming work
- [ ] Identify data dependencies between stories
- [ ] Identify feature dependencies between epics
- [ ] Map critical path through epics
- [ ] Identify parallel work opportunities
- [ ] Create dependency graph output
- [ ] Provide specific recommendations

## Example Analysis

```markdown
# Epic Dependency Analysis - 2025-11-04

## Current Status
- Completed: Epic 1 Stories 1.1, 1.2, 1.3 (profiles done)
- In Progress: None
- Next: Story 1.4 or parallel work

## Key Insights

### Epic 1 → Epic 2 Dependency
Epic 2 (Signal Detection) REQUIRES:
- Story 1.2: Data schema ✅
- Story 1.4: Transaction data (NEEDED NEXT)
- Story 1.5: Liability data (NEEDED NEXT)

**Blocker:** Epic 2 cannot start until 1.4 is done (needs transactions to detect signals)

### Parallelization Opportunity: Epic 5
Epic 5 (Consent & Guardrails) has ZERO dependencies on Epic 2, 3, 4
- Can start NOW after Epic 1
- Provides value to all future epics
- Independent codebase (spendsense/guardrails/)

### Recommendation
**Best Strategy for 1 developer:**
1. Complete Story 1.4 (transactions)
2. Complete Story 1.5 (liabilities)
3. Then SPLIT: Start Epic 2 AND Epic 5 stories in alternating sprints

**Best Strategy for 2 developers:**
- Dev A: Continue Epic 1 (1.4, 1.5, 1.6)
- Dev B: Start Epic 5 (5.1, 5.2) in parallel

This maximizes velocity and reduces future bottlenecks.
```

## Integration with Other Skills

- Use AFTER `/BMad:bmm:workflows:retrospective` for epic completion
- Use BEFORE `/BMad:bmm:workflows:sprint-planning` for next sprint
- Use WITH `story-validation-guide` when completing final story of epic

## Principles

- **Read, don't assume**: Always read actual files
- **Visualize dependencies**: Use ASCII graphs when helpful
- **Think critically**: Don't just list epics in order, find TRUE dependencies
- **Optimize for team**: Consider 1, 2, 3+ developer scenarios
- **Be actionable**: Give specific "start this next" recommendations
