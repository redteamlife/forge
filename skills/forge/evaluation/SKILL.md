---
name: evaluation
description: Apply FORGE definition-of-done and evidence checks to a task. Use when verifying completion gates, required testing, documentation updates, and whether the task is eligible to be marked complete and committed.
---

# FORGE Evaluation

Use this skill to decide whether a task is actually complete.

## Evaluate

- task scope is satisfied without unrelated work
- required validation was run
- critique pass is complete
- security review is complete
- required docs are updated
- task status and Conventional Commit metadata are ready
- commit message is free of AI attribution or tool-marketing lines
- in team mode, task claim, branch, reviewer, and PR metadata are consistent
- in solo mode, the task is ready to be marked `complete` and committed with a Conventional Commit before any new task starts

## Evidence

Prefer storing structured evidence in `docs/forge/EVALUATION.md`.

If the project uses CI enforcement, confirm that the expected artifacts are updated in the same change set.
In team mode, prefer task-scoped append-only entries over rewriting shared narrative summaries.

Keep evaluation output compact: gate result first, short evidence notes second.
