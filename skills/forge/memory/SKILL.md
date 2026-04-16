---
name: forge-memory
description: Read and maintain FORGE project memory across sessions. Use when retrieving recent patterns or failures before implementation, or when appending concise lessons, failure notes, and guardrail refinements after a task attempt.
---

# FORGE Memory

Use this skill to keep long-lived lessons out of the main prompt flow.

## Read Pattern

1. Start with the most recent, highest-signal entries.
2. Only load older detail when the current task matches the same component or failure mode.
3. Do not read the full memory file when recent entries are sufficient.

## Write Pattern

After a task attempt:

- record a short recent entry
- record a fuller pattern or failure entry only if it adds future reuse value
- keep entries factual, brief, and attributable to a concrete task
- in team mode, include actor, branch, and task id so future agents can tell parallel work apart

This skill exists mainly to save tokens while preserving operational learning.
