---
name: kanban
description: Comprehensive guide to Kanban workflows in Hermes including orchestrator playbooks, worker pitfalls, decomposition, and specialist roster conventions
category: devops
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [kanban, orchestrator, worker, decomposition, routing]
    related_skills: [systematic-debugging, plan]
---

# Kanban Workflows in Hermes

Complete guide to using Kanban for task decomposition, orchestration, and worker execution in Hermes environments.

## Overview

This skill consolidates Kanban-related functionalities into a comprehensive framework covering:
- Kanban orchestrator playbook and decomposition procedures
- Kanban worker pitfalls, examples, and edge cases
- Specialist roster conventions and anti-temptation rules
- Task creation, linking, and completion patterns
- Recovery procedures for stuck workers
- Integration with Hermes delegation and planning systems

## When to Use

Use this skill when you need to:
- Decompose complex tasks into specialist workflows using Kanban
- Orchestrate multi-agent workflows with proper routing and dependencies
- Understand and avoid common pitfalls for Kanban workers
- Set up and manage specialist rosters (researcher, analyst, writer, etc.)
- Create and manage Kanban tasks with proper parent/child relationships
- Recover stuck or hallucinating worker profiles
- Integrate Kanban with other Hermes skills like delegation and planning

## Core Components

### 1. Kanban Orchestrator Playbook
Decomposition procedures, task graph creation, and routing rules for orchestrator profiles.

### 2. Kanban Worker Guidance
Pitfalls, examples, and edge cases for workers executing Kanban tasks.

### 3. Specialist Roster Conventions
Standard profiles (researcher, analyst, writer, backend-eng, frontend-eng, ops, pm, reviewer) and their typical workspaces.

### 4. Anti-Temptation Rules
Rules enforcing the "route, don't execute" principle for orchestrators.

### 5. Task Linking and Dependencies
Proper use of `kanban_create`, `kanban_link`, and `kanban_complete` with parent/child relationships.

### 6. Worker Recovery Procedures
Reclaim, reassign, and model change procedures for stuck workers.

## Quick Reference

| Component | Purpose | Key Concepts |
|-----------|---------|--------------|
| **Orchestrator** | Decompose and route work | Task graph, decomposition playbook, anti-temptation rules |
| **Worker** | Execute tasks safely | Pitfalls, examples, edge cases, recovery procedures |
| **Specialist Roster** | Standard profiles | Researcher, analyst, writer, backend-eng, frontend-eng, ops, pm, reviewer |
| **Task Lifecycle** | Create → Link → Complete | Parent gating, fan-out/fan-in patterns, human-in-the-loop |
| **Recovery** | Fix stuck workers | Reclaim, reassign, change profile model |

## Environment Setup

Before using Kanban workflows, ensure:
1. Hermes environment is properly configured with Kanban guidance auto-injected
2. You understand the difference between orchestrator and worker roles
3. You have access to the `kanban_create`, `kanban_link`, and `kanban_complete` functions
4. You know when to use Kanban vs. direct delegation (`delegate_task`)

## Common Patterns

### Fan-Out + Fan-In (Research → Synthesize)
N researcher tasks with no parents, one analyst task with all as parents.

### Pipeline with Gates
PM → Backend-eng → Reviewer, each stage gated by parent completion.

### Same-Profile Queue
Multiple tasks assigned to the same profile (e.g., 50 translator tasks) processed serially.

### Human-in-the-Loop
Tasks can `kanban_block()` to wait for user input, then respawn after `/unblock`.

## Verification

After setting up any Kanban workflow:
1. Test task creation and linking in a safe environment
2. Verify parent/child dependencies work correctly
3. Check that orchestrator follows anti-temptation rules
4. Confirm worker recovery procedures function as expected
5. Monitor dashboard for proper task progression

## Maintenance

- Keep Kanban conventions updated as specialist rosters evolve
- Test recovery procedures periodically
- Update anti-temptation rules based on observed orchestrator behavior
- Document new patterns and pitfalls as they emerge

## Related Skills

- `systematic-debugging`: For diagnosing issues in Kanban workflows
- `plan`: For creating markdown plans when execution is not needed
- `devops/uv-package-installation`: For installing packages in restricted environments
- `autonomous-ai-agents/hermes-agent`: For configuring and extending Hermes Agent

---

## Subsections

The following sections detail specific aspects of Kanban workflows that were previously separate skills:

### Kanban Orchestrator — Decomposition Playbook
See the original `kanban-orchestrator` skill for complete details on orchestrator role, decomposition playbook, specialist roster conventions, anti-temptation rules, task linking patterns, and worker recovery procedures.

### Kanban Worker Pitfalls and Guidance
See the original `kanban-worker` skill for detailed pitfalls, examples, and edge cases for Hermes Kanban workers, including lifecycle guidance and scenario-specific advice.

---
*This skill consolidates multiple Kanban-related skills into a comprehensive framework for easier discovery and maintenance.*