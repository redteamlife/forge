---
name: forge-memory
description: Read and maintain FORGE project memory across sessions. Use when retrieving recent patterns or failures before implementation, or when appending concise lessons, failure notes, and guardrail refinements after a task attempt.
---

# FORGE Memory

Use this skill to keep long-lived lessons out of the main prompt flow.

## Read Pattern

1. Do not read memory at startup.
2. Read `docs/forge/MEMORY.index.yaml` first when present.
3. Read only the relevant file under `docs/forge/memory/`.
4. Fall back to recent high-signal entries in `MEMORY.md` when split memory is absent.
5. Do not read the full memory file when a smaller topic file or recent entries are sufficient.

## Write Pattern

After a task attempt:

- record a short recent entry
- record a fuller pattern or failure entry only if it adds future reuse value
- keep entries factual, brief, and attributable to a concrete task
- in team mode, include actor, branch, and task id so future agents can tell parallel work apart
- use the project-local entry shape when memory docs define one
- prefer `contract-conflict` or `coordination-incident` entries for reusable interface or parallel-work failures
- if a `max_entries` value is present, consolidate oldest entries before exceeding it
- summarize and deduplicate before appending

This skill exists mainly to save tokens while preserving operational learning.
