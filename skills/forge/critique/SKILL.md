---
name: forge-critique
description: Run the FORGE critique pass for a completed or in-progress task. Use when checking for scope drift, undocumented assumptions, architecture conflicts, missing docs, or unaddressed failure modes before marking a task complete.
---

# FORGE Critique

Review the change strictly through the lens of bounded execution.

## Checks

- Did the work exceed the selected task?
- Are assumptions and deferred issues explicit?
- Are edge cases or failure modes left unaddressed?
- Does the change conflict with architecture or documented constraints?
- Were required docs updated?
- In team mode, do branch, claim, and file-scope records still match the actual work?

## Output

Produce a concise pass/fail style critique with:

- blocking findings
- non-blocking notes
- whether the task may proceed to security review and evaluation
- whether the task metadata remains consistent for a PR-based merge

Keep the critique short. Prefer a few findings over a narrative review.
Use findings-first output. Avoid explanatory recap when a short finding line is enough.

If there are blocking issues, stop rather than softening the conclusion.
